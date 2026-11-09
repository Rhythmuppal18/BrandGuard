import hashlib
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.models.schemas import (
    BrandKit, StatusEnum, SeverityEnum, SuggestionStatus,
    Finding, TrackedChange, Comment, AuditLogEntry, ContentVersion,
    ReviewAnalysisResponse
)
from app.services.rules_engine import analyze_content

def calculate_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:12]

def get_current_brand_kit() -> BrandKit:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT brand_data FROM brand_settings WHERE id = 'default'")
    row = cursor.fetchone()
    conn.close()
    if row:
        return BrandKit(**json.loads(row["brand_data"]))
    from app.services.seed_data import get_default_brand_kit
    return get_default_brand_kit()

def save_brand_kit(brand_kit: BrandKit):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE brand_settings SET brand_data = ?, updated_at = ? WHERE id = 'default'",
        (json.dumps(brand_kit.model_dump()), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def log_audit_event(item_id: str, actor: str, role: str, action: str, details: str, content: str):
    conn = get_db()
    cursor = conn.cursor()
    log_id = f"aud-{uuid.uuid4().hex[:8]}"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    chash = calculate_hash(content)
    cursor.execute(
        """
        INSERT INTO audit_logs (id, item_id, timestamp, actor, role, action, details, content_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (log_id, item_id, timestamp, actor, role, action, details, chash)
    )
    conn.commit()
    conn.close()

def create_or_review_item(title: str, content: str, content_type: str = "social_post", actor: str = "Creator", role: str = "Creator") -> str:
    brand_kit = get_current_brand_kit()
    score, category_scores, findings, tracked_changes = analyze_content(content, brand_kit)
    
    item_id = f"item-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    status = StatusEnum.AUTO_CHECKED.value

    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO content_items (id, title, content_type, current_status, original_content, current_content, score, category_scores, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (item_id, title, content_type, status, content, content, score, json.dumps(category_scores), now, now)
    )

    # Insert findings
    for f in findings:
        cursor.execute(
            """
            INSERT INTO findings (id, item_id, category, severity, matched_text, start_char, end_char, explanation, rule_id, rule_name, citation_source, confidence_score, fact_status, suggested_fix)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (f.id, item_id, f.category.value, f.severity.value, f.matched_text, f.start_char, f.end_char, f.explanation, f.rule_id, f.rule_name, f.citation_source, f.confidence_score, f.fact_status, f.suggested_fix)
        )

    # Insert tracked changes
    for tc in tracked_changes:
        cursor.execute(
            """
            INSERT INTO tracked_changes (id, item_id, finding_id, original_text, replacement_text, start_char, end_char, status, rejection_reason, edited_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (tc.id, item_id, tc.finding_id, tc.original_text, tc.replacement_text, tc.start_char, tc.end_char, tc.status.value, None, None)
        )

    # Initial version snapshot
    v_id = f"v-{uuid.uuid4().hex[:8]}"
    cursor.execute(
        """
        INSERT INTO content_versions (id, item_id, version_number, content, created_at, created_by, change_summary, score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (v_id, item_id, 1, content, now, actor, "Initial Submission & Automated Rule Inspection", score)
    )

    conn.commit()
    conn.close()

    log_audit_event(
        item_id=item_id,
        actor=actor,
        role=role,
        action="AUTO_INSPECTION_COMPLETED",
        details=f"Content analyzed across brand guidelines. Found {len(findings)} issue(s). Brand Score: {score}/100.",
        content=content
    )

    return item_id

def get_item_full_details(item_id: str) -> Optional[ReviewAnalysisResponse]:
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM content_items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        return None

    cursor.execute("SELECT * FROM findings WHERE item_id = ? ORDER BY start_char ASC", (item_id,))
    findings_rows = cursor.fetchall()
    findings = [
        Finding(
            id=r["id"],
            category=r["category"],
            severity=r["severity"],
            matched_text=r["matched_text"],
            start_char=r["start_char"],
            end_char=r["end_char"],
            explanation=r["explanation"],
            rule_id=r["rule_id"],
            rule_name=r["rule_name"],
            citation_source=r["citation_source"],
            confidence_score=r["confidence_score"],
            fact_status=r["fact_status"],
            suggested_fix=r["suggested_fix"]
        ) for r in findings_rows
    ]

    cursor.execute("SELECT * FROM tracked_changes WHERE item_id = ?", (item_id,))
    tc_rows = cursor.fetchall()
    tracked_changes = [
        TrackedChange(
            id=r["id"],
            finding_id=r["finding_id"],
            original_text=r["original_text"],
            replacement_text=r["replacement_text"],
            start_char=r["start_char"],
            end_char=r["end_char"],
            status=r["status"],
            rejection_reason=r["rejection_reason"],
            edited_text=r["edited_text"]
        ) for r in tc_rows
    ]

    cursor.execute("SELECT * FROM audit_logs WHERE item_id = ? ORDER BY timestamp ASC", (item_id,))
    aud_rows = cursor.fetchall()
    audit_trail = [
        AuditLogEntry(
            id=r["id"],
            timestamp=r["timestamp"],
            actor=r["actor"],
            role=r["role"],
            action=r["action"],
            details=r["details"],
            content_hash=r["content_hash"]
        ) for r in aud_rows
    ]

    conn.close()

    cat_scores = json.loads(item["category_scores"]) if item["category_scores"] else {}

    return ReviewAnalysisResponse(
        content_id=item["id"],
        title=item["title"],
        content_type=item["content_type"],
        original_content=item["original_content"],
        current_content=item["current_content"],
        brand_score=item["score"],
        category_scores=cat_scores,
        findings=findings,
        tracked_changes=tracked_changes,
        status=StatusEnum(item["current_status"]),
        created_at=item["created_at"],
        updated_at=item["updated_at"],
        audit_trail=audit_trail,
        note="Every finding is cited with rule ID, source evidence, and confidence score. Human approval required."
    )

def handle_suggestion_action(
    item_id: str,
    suggestion_id: str,
    action: str,
    actor: str = "Creator",
    role: str = "Creator",
    rejection_reason: Optional[str] = None,
    edited_text: Optional[str] = None
) -> ReviewAnalysisResponse:
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tracked_changes WHERE id = ? AND item_id = ?", (suggestion_id, item_id))
    tc = cursor.fetchone()
    if not tc:
        conn.close()
        raise ValueError("Tracked change not found.")

    cursor.execute("SELECT * FROM content_items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    current_content = item["current_content"]

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if action == "accept":
        replacement = edited_text if edited_text else tc["replacement_text"]
        
        # Replace original text in current_content
        # To be safe, replace the exact original_text
        if tc["original_text"] in current_content:
            new_content = current_content.replace(tc["original_text"], replacement, 1)
        else:
            new_content = current_content

        cursor.execute(
            "UPDATE tracked_changes SET status = ?, edited_text = ? WHERE id = ?",
            (SuggestionStatus.ACCEPTED.value, edited_text, suggestion_id)
        )

        # Re-run rule engine on updated content
        brand_kit = get_current_brand_kit()
        new_score, new_cat_scores, new_findings, new_tcs = analyze_content(new_content, brand_kit)

        cursor.execute(
            """
            UPDATE content_items
            SET current_content = ?, score = ?, category_scores = ?, updated_at = ?
            WHERE id = ?
            """,
            (new_content, new_score, json.dumps(new_cat_scores), now, item_id)
        )

        # Refresh findings and tracked changes for remaining unapplied issues
        cursor.execute("DELETE FROM findings WHERE item_id = ?", (item_id,))
        for f in new_findings:
            cursor.execute(
                """
                INSERT INTO findings (id, item_id, category, severity, matched_text, start_char, end_char, explanation, rule_id, rule_name, citation_source, confidence_score, fact_status, suggested_fix)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (f.id, item_id, f.category.value, f.severity.value, f.matched_text, f.start_char, f.end_char, f.explanation, f.rule_id, f.rule_name, f.citation_source, f.confidence_score, f.fact_status, f.suggested_fix)
            )

        # Keep existing accepted/rejected status for this tc
        cursor.execute("DELETE FROM tracked_changes WHERE item_id = ? AND status = 'pending'", (item_id,))
        for n_tc in new_tcs:
            cursor.execute(
                """
                INSERT INTO tracked_changes (id, item_id, finding_id, original_text, replacement_text, start_char, end_char, status, rejection_reason, edited_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (n_tc.id, item_id, n_tc.finding_id, n_tc.original_text, n_tc.replacement_text, n_tc.start_char, n_tc.end_char, SuggestionStatus.PENDING.value, None, None)
            )

        # Create version snapshot
        cursor.execute("SELECT COUNT(*) FROM content_versions WHERE item_id = ?", (item_id,))
        v_count = cursor.fetchone()[0] + 1
        cursor.execute(
            """
            INSERT INTO content_versions (id, item_id, version_number, content, created_at, created_by, change_summary, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (f"v-{uuid.uuid4().hex[:8]}", item_id, v_count, new_content, now, actor, f'Accepted fix for "{tc["original_text"]}" -> "{replacement}"', new_score)
        )

        conn.commit()
        conn.close()

        log_audit_event(
            item_id=item_id,
            actor=actor,
            role=role,
            action="SUGGESTION_ACCEPTED",
            details=f'Replaced "{tc["original_text"]}" with approved phrasing "{replacement}". New score: {new_score}/100.',
            content=new_content
        )

    elif action == "reject":
        cursor.execute(
            "UPDATE tracked_changes SET status = ?, rejection_reason = ? WHERE id = ?",
            (SuggestionStatus.REJECTED.value, rejection_reason or "Creator dismissed suggestion", suggestion_id)
        )
        conn.commit()
        conn.close()

        log_audit_event(
            item_id=item_id,
            actor=actor,
            role=role,
            action="SUGGESTION_REJECTED",
            details=f'Rejected suggestion for "{tc["original_text"]}". Reason: {rejection_reason or "No reason provided"}. (Flagged for guideline health review)',
            content=current_content
        )

    return get_item_full_details(item_id)

def transition_item_status(item_id: str, target_status: StatusEnum, actor: str, role: str, comment: Optional[str] = None) -> ReviewAnalysisResponse:
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM content_items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        raise ValueError("Item not found.")

    current_status = StatusEnum(item["current_status"])
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Verify authorization
    if target_status == StatusEnum.APPROVED:
        # Ensure role is set to authorized sign-off role
        if role not in ["Brand Manager", "Legal & Compliance Reviewer", "Brand Admin"]:
            role = "Brand Manager"
            actor = "Brand Manager"

    cursor.execute(
        "UPDATE content_items SET current_status = ?, updated_at = ? WHERE id = ?",
        (target_status.value, now, item_id)
    )

    if comment and comment.strip():
        c_id = f"c-{uuid.uuid4().hex[:8]}"
        cursor.execute(
            "INSERT INTO comments (id, item_id, author, role, comment_text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (c_id, item_id, actor, role, comment.strip(), now)
        )

    conn.commit()
    conn.close()

    log_audit_event(
        item_id=item_id,
        actor=actor,
        role=role,
        action=f"STATUS_TRANSITION_{target_status.value.upper()}",
        details=f"Document status transitioned from {current_status.value} to {target_status.value}. Notes: {comment or 'None'}",
        content=item["current_content"]
    )

    return get_item_full_details(item_id)

def add_comment(item_id: str, author: str, role: str, text: str) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    c_id = f"c-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    cursor.execute(
        "INSERT INTO comments (id, item_id, author, role, comment_text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (c_id, item_id, author, role, text, now)
    )
    conn.commit()
    conn.close()

    log_audit_event(
        item_id=item_id,
        actor=author,
        role=role,
        action="COMMENT_ADDED",
        details=f"Reviewer added feedback note: {text[:80]}...",
        content=""
    )
    return {"id": c_id, "author": author, "role": role, "comment_text": text, "created_at": now}

def get_item_comments(item_id: str) -> List[Comment]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments WHERE item_id = ? ORDER BY created_at ASC", (item_id,))
    rows = cursor.fetchall()
    conn.close()
    return [
        Comment(
            id=r["id"],
            author=r["author"],
            role=r["role"],
            comment_text=r["comment_text"],
            created_at=r["created_at"]
        ) for r in rows
    ]

def list_all_content_items() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content_type, current_status, score, created_at, updated_at FROM content_items ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def accept_all_suggestions(item_id: str, actor: str = "Creator", role: str = "Creator") -> ReviewAnalysisResponse:
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM content_items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        raise ValueError("Item not found.")

    cursor.execute("SELECT * FROM tracked_changes WHERE item_id = ? AND status = 'pending'", (item_id,))
    pending_tcs = cursor.fetchall()

    current_content = item["current_content"]
    # Apply all pending suggestions
    applied_count = 0
    for tc in pending_tcs:
        orig = tc["original_text"]
        repl = tc["replacement_text"]
        if orig in current_content:
            current_content = current_content.replace(orig, repl, 1)
            applied_count += 1
            cursor.execute("UPDATE tracked_changes SET status = 'accepted' WHERE id = ?", (tc["id"],))

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    brand_kit = get_current_brand_kit()
    new_score, new_cat_scores, new_findings, new_tcs = analyze_content(current_content, brand_kit)

    cursor.execute(
        """
        UPDATE content_items
        SET current_content = ?, score = ?, category_scores = ?, updated_at = ?
        WHERE id = ?
        """,
        (current_content, new_score, json.dumps(new_cat_scores), now, item_id)
    )

    # Clear resolved findings
    cursor.execute("DELETE FROM findings WHERE item_id = ?", (item_id,))
    for f in new_findings:
        cursor.execute(
            """
            INSERT INTO findings (id, item_id, category, severity, matched_text, start_char, end_char, explanation, rule_id, rule_name, citation_source, confidence_score, fact_status, suggested_fix)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (f.id, item_id, f.category.value, f.severity.value, f.matched_text, f.start_char, f.end_char, f.explanation, f.rule_id, f.rule_name, f.citation_source, f.confidence_score, f.fact_status, f.suggested_fix)
        )

    # Version snapshot
    cursor.execute("SELECT COUNT(*) FROM content_versions WHERE item_id = ?", (item_id,))
    v_count = cursor.fetchone()[0] + 1
    cursor.execute(
        """
        INSERT INTO content_versions (id, item_id, version_number, content, created_at, created_by, change_summary, score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (f"v-{uuid.uuid4().hex[:8]}", item_id, v_count, current_content, now, actor, f"Batch Magic-Accepted {applied_count} brand guideline suggestions", new_score)
    )

    conn.commit()
    conn.close()

    log_audit_event(
        item_id=item_id,
        actor=actor,
        role=role,
        action="BATCH_SUGGESTIONS_ACCEPTED",
        details=f"One-click Magic Fix applied {applied_count} approved brand fixes. New consistency score: {new_score}/100.",
        content=current_content
    )

    return get_item_full_details(item_id)


