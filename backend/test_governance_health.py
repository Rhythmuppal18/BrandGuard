from app.services.governance_health_service import (
    get_rule_dispute_analytics,
    get_conflicting_guidelines,
    get_clarification_proposals,
    apply_clarification_proposal,
    rollback_clarification_proposal,
    record_rule_dispute,
    get_governance_metrics
)
from app.core.database import get_db

def test_governance_health_suite():
    print("========================================")
    print(" RUNNING PILLAR 3 GOVERNANCE TESTS     ")
    print("========================================")

    # 1. Dispute Analytics Test
    print("Testing Statistical Rule Dispute Analytics...")
    stats = get_rule_dispute_analytics()
    assert len(stats) >= 4, "Expected at least 4 analyzed rules"
    top_rule = stats[0]
    print(f"  ✓ High Friction Rule Identified: {top_rule.rule_id} ({top_rule.rule_name})")
    print(f"  ✓ Friction Index: {top_rule.friction_index}/10.0 | Dispute Rate: {top_rule.dispute_rate_pct}%")
    assert top_rule.friction_index > 0.0

    # 2. Conflicting Guideline Detection Test
    print("Testing Conflicting Guideline & Contradiction Detection...")
    conflicts = get_conflicting_guidelines()
    assert len(conflicts) >= 3, "Expected at least 3 active guideline conflicts"
    critical_conflicts = [c for c in conflicts if c.severity == "CRITICAL"]
    assert len(critical_conflicts) >= 2, "Expected critical conflicts detected"
    print(f"  ✓ Total Conflicts: {len(conflicts)} (Critical: {len(critical_conflicts)})")
    print(f"  ✓ Example Collision: '{conflicts[0].rule_a_id}' vs '{conflicts[0].rule_b_id}'")

    # 3. AI Clarification Proposals and Self-Healing
    print("Testing AI-Assisted Self-Healing Proposals...")
    proposals = get_clarification_proposals()
    assert len(proposals) >= 2, "Expected at least 2 clarification proposals"
    prop = proposals[0]
    print(f"  ✓ Proposal: '{prop.title}' (Confidence: {prop.confidence_score}%)")

    # Apply Proposal with RBAC (Creator rejected, Admin permitted)
    print("Testing RBAC on Proposal Approval & Self-Healing...")
    try:
        apply_clarification_proposal(prop.id, admin_user="Creator", user_role="CREATOR")
        assert False, "Should have raised PermissionError for CREATOR role!"
    except PermissionError as e:
        print(f"  ✓ Correctly rejected unauthorized proposal application: {str(e)[:45]}...")

    apply_res = apply_clarification_proposal(prop.id, admin_user="Chief Compliance Officer", user_role="ADMIN")
    assert apply_res["success"] is True
    print(f"  ✓ {apply_res['message']} (Guideline Snapshot #{apply_res['version_number']})")

    # Check that linked conflict was resolved in persistent database
    updated_conflicts = get_conflicting_guidelines()
    resolved_linked = [c for c in updated_conflicts if c.id == prop.conflict_id]
    if resolved_linked:
        assert resolved_linked[0].status == "RESOLVED"
        print(f"  ✓ Linked Conflict {resolved_linked[0].id} resolved automatically in DB!")

    # Rollback Proposal
    print("Testing Governance Rollback Safety Mechanism...")
    rollback_res = rollback_clarification_proposal(prop.id, admin_user="Chief Compliance Officer", user_role="ADMIN")
    assert rollback_res["success"] is True
    print(f"  ✓ {rollback_res['message']} (Rollback Snapshot #{rollback_res['version_number']})")

    # 4. Record Live Dispute Event to SQLite
    print("Testing Live Dispute Event Submission to SQLite...")
    disp = record_rule_dispute(
        rule_id="RULE-TONE-01",
        rule_name="Celebratory & Empowering Voice Directive",
        category="Tone & Voice",
        reason="Creator testing live dispute filing during incident announcement",
        user_role="Content Creator"
    )
    assert disp.id.startswith("disp-")

    # Verify dispute persisted in SQLite directly
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM governance_disputes WHERE id = ?", (disp.id,))
    row = cursor.fetchone()
    conn.close()
    assert row is not None, "Dispute failed to persist in SQLite!"
    print(f"  ✓ Live Dispute Recorded & Persisted: {disp.id} for rule {disp.rule_id}")

    # 5. Governance Velocity & Real Calculated Performance Metrics
    print("Testing Real Derived Governance Metrics...")
    metrics = get_governance_metrics()
    assert 50 <= metrics.overall_health_score <= 100
    assert metrics.mean_time_to_approval_hours > 0.0
    assert metrics.mtta_reduction_pct > 0.0
    assert metrics.total_disputes_recorded >= 5
    print(f"  ✓ Guideline Health Score: {metrics.overall_health_score}/100")
    print(f"  ✓ Real MTTA: {metrics.mean_time_to_approval_hours} hrs ({metrics.mtta_reduction_pct}% reduction vs standard 48h SLA)")
    print(f"  ✓ Total Disputes Recorded: {metrics.total_disputes_recorded} (Real count from SQLite)")
    print("========================================")
    print(" ALL PILLAR 3 GOVERNANCE TESTS PASSED!  ")
    print("========================================")

if __name__ == "__main__":
    test_governance_health_suite()
