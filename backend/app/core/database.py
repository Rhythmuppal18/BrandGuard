import sqlite3
import json
from datetime import datetime
from app.core.config import DB_PATH, DEFAULT_TENANT_ID
from app.services.seed_data import get_default_brand_kit

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Enable WAL mode for high performance
    cursor.execute("PRAGMA journal_mode=WAL;")

    # Safe Schema Migrations for existing database
    cursor.execute("PRAGMA table_info(content_items)")
    content_cols = [col[1] for col in cursor.fetchall()]
    if content_cols and "tenant_id" not in content_cols:
        cursor.execute("ALTER TABLE content_items ADD COLUMN tenant_id TEXT DEFAULT 'tenant-apexpay-prod'")
    if content_cols and "approved_at" not in content_cols:
        cursor.execute("ALTER TABLE content_items ADD COLUMN approved_at TEXT")

    cursor.execute("PRAGMA table_info(brand_settings)")
    brand_cols = [col[1] for col in cursor.fetchall()]
    if brand_cols and "tenant_id" not in brand_cols:
        cursor.execute("ALTER TABLE brand_settings ADD COLUMN tenant_id TEXT DEFAULT 'tenant-apexpay-prod'")

    # 1. Core Brand Kit Settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brand_settings (
        id TEXT PRIMARY KEY,
        brand_data TEXT,
        updated_at TEXT,
        tenant_id TEXT DEFAULT 'tenant-apexpay-prod'
    );
    """)

    # 2. Content Items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS content_items (
        id TEXT PRIMARY KEY,
        title TEXT,
        content_type TEXT,
        current_status TEXT,
        original_content TEXT,
        current_content TEXT,
        score INTEGER,
        category_scores TEXT,
        created_at TEXT,
        updated_at TEXT,
        approved_at TEXT,
        tenant_id TEXT DEFAULT 'tenant-apexpay-prod'
    );
    """)

    # 3. Rule Findings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS findings (
        id TEXT PRIMARY KEY,
        item_id TEXT,
        category TEXT,
        severity TEXT,
        matched_text TEXT,
        start_char INTEGER,
        end_char INTEGER,
        explanation TEXT,
        rule_id TEXT,
        rule_name TEXT,
        citation_source TEXT,
        confidence_score INTEGER,
        fact_status TEXT,
        suggested_fix TEXT,
        FOREIGN KEY (item_id) REFERENCES content_items(id) ON DELETE CASCADE
    );
    """)

    # 4. Tracked Changes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tracked_changes (
        id TEXT PRIMARY KEY,
        item_id TEXT,
        finding_id TEXT,
        original_text TEXT,
        replacement_text TEXT,
        start_char INTEGER,
        end_char INTEGER,
        status TEXT,
        rejection_reason TEXT,
        edited_text TEXT,
        FOREIGN KEY (item_id) REFERENCES content_items(id) ON DELETE CASCADE
    );
    """)

    # 5. Editorial Comments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id TEXT PRIMARY KEY,
        item_id TEXT,
        author TEXT,
        role TEXT,
        comment_text TEXT,
        created_at TEXT,
        FOREIGN KEY (item_id) REFERENCES content_items(id) ON DELETE CASCADE
    );
    """)

    # 6. Audit Logs with Full SHA-256 Hashes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        item_id TEXT,
        timestamp TEXT,
        actor TEXT,
        role TEXT,
        action TEXT,
        details TEXT,
        content_hash TEXT,
        FOREIGN KEY (item_id) REFERENCES content_items(id) ON DELETE CASCADE
    );
    """)

    # 7. Content Versions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS content_versions (
        id TEXT PRIMARY KEY,
        item_id TEXT,
        version_number INTEGER,
        content TEXT,
        created_at TEXT,
        created_by TEXT,
        change_summary TEXT,
        score INTEGER,
        FOREIGN KEY (item_id) REFERENCES content_items(id) ON DELETE CASCADE
    );
    """)

    # 8. Persistent Secure Privacy Vault (Reversible Redaction Mappings)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS privacy_vault (
        scan_id TEXT,
        placeholder TEXT,
        encrypted_original TEXT,
        created_at TEXT,
        tenant_id TEXT DEFAULT 'tenant-apexpay-prod',
        PRIMARY KEY (scan_id, placeholder)
    );
    """)

    # 9. Verifiable Tamper-Evident Hash-Chained AI Disclosure Ledger
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_disclosure_ledger (
        id TEXT PRIMARY KEY,
        block_height INTEGER,
        prev_hash TEXT,
        block_hash TEXT,
        timestamp TEXT,
        execution_mode TEXT,
        model_identifier TEXT,
        prompt_hash TEXT,
        response_hash TEXT,
        redaction_count INTEGER,
        sensitive_categories TEXT,
        latency_ms REAL,
        status TEXT,
        tenant_id TEXT DEFAULT 'tenant-apexpay-prod'
    );
    """)

    # 10. Persistent Governance Disputes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS governance_disputes (
        id TEXT PRIMARY KEY,
        rule_id TEXT,
        rule_name TEXT,
        category TEXT,
        user_role TEXT,
        actor_id TEXT,
        reason TEXT,
        timestamp TEXT,
        status TEXT,
        tenant_id TEXT DEFAULT 'tenant-apexpay-prod'
    );
    """)

    # 11. Persistent Governance Conflicts (Policy Collision Matrix)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS governance_conflicts (
        id TEXT PRIMARY KEY,
        rule_a_id TEXT,
        rule_a_name TEXT,
        rule_a_excerpt TEXT,
        rule_b_id TEXT,
        rule_b_name TEXT,
        rule_b_excerpt TEXT,
        severity TEXT,
        impact_description TEXT,
        status TEXT,
        resolved_at TEXT,
        tenant_id TEXT DEFAULT 'tenant-apexpay-prod'
    );
    """)

    # 12. Persistent Guideline Self-Healing Proposals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS governance_proposals (
        id TEXT PRIMARY KEY,
        conflict_id TEXT,
        target_rule_ids TEXT,
        title TEXT,
        original_text TEXT,
        proposed_clarification TEXT,
        rationale TEXT,
        estimated_dispute_reduction_pct INTEGER,
        confidence_score INTEGER,
        status TEXT,
        created_at TEXT,
        applied_at TEXT,
        applied_by TEXT,
        tenant_id TEXT DEFAULT 'tenant-apexpay-prod'
    );
    """)

    # 13. Guideline History & Version Tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS guideline_versions (
        id TEXT PRIMARY KEY,
        version_num INTEGER,
        guidelines_json TEXT,
        change_summary TEXT,
        created_at TEXT,
        author TEXT,
        tenant_id TEXT DEFAULT 'tenant-apexpay-prod'
    );
    """)

    # Check if brand_settings is seeded
    cursor.execute("SELECT id FROM brand_settings WHERE id = 'default'")
    if not cursor.fetchone():
        default_kit = get_default_brand_kit()
        cursor.execute(
            "INSERT INTO brand_settings (id, brand_data, updated_at, tenant_id) VALUES (?, ?, ?, ?)",
            ('default', json.dumps(default_kit.model_dump()), datetime.utcnow().isoformat(), DEFAULT_TENANT_ID)
        )

    # Initial genesis block for AI Disclosure Ledger if empty
    cursor.execute("SELECT COUNT(*) FROM ai_disclosure_ledger")
    if cursor.fetchone()[0] == 0:
        genesis_prev = "0" * 64
        genesis_ts = datetime.utcnow().isoformat()
        import hashlib
        genesis_payload = f"0|{genesis_prev}|{genesis_ts}|GENESIS_BLOCK"
        genesis_hash = hashlib.sha256(genesis_payload.encode("utf-8")).hexdigest()
        cursor.execute("""
        INSERT INTO ai_disclosure_ledger
        (id, block_height, prev_hash, block_hash, timestamp, execution_mode, model_identifier, prompt_hash, response_hash, redaction_count, sensitive_categories, latency_ms, status, tenant_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "ledg-genesis",
            0,
            genesis_prev,
            genesis_hash,
            genesis_ts,
            "GENESIS_INITIALIZATION",
            "BrandGuard-Ledger-Genesis",
            genesis_hash,
            genesis_hash,
            0,
            json.dumps([]),
            0.0,
            "IMMUTABLE_GENESIS",
            DEFAULT_TENANT_ID
        ))

    conn.commit()
    conn.close()

# Ensure tables are initialized on import
try:
    init_db()
except Exception:
    pass

