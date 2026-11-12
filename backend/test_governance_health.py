from app.services.governance_health_service import (
    get_rule_dispute_analytics,
    get_conflicting_guidelines,
    get_clarification_proposals,
    apply_clarification_proposal,
    rollback_clarification_proposal,
    record_rule_dispute,
    get_governance_metrics
)

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
    print(f"  ✓ Top Rejection Reasons: {len(top_rule.top_dispute_reasons)} logged")
    assert top_rule.friction_index > 0.0

    # 2. Conflicting Guideline Detection Test
    print("Testing Conflicting Guideline & Contradiction Detection...")
    conflicts = get_conflicting_guidelines()
    assert len(conflicts) >= 3, "Expected at least 3 active guideline conflicts"
    critical_conflicts = [c for c in conflicts if c.severity == "CRITICAL"]
    assert len(critical_conflicts) >= 2, "Expected critical conflicts detected"
    print(f"  ✓ Total Conflicts: {len(conflicts)} (Critical: {len(critical_conflicts)})")
    print(f"  ✓ Example Collision: '{conflicts[0].rule_a_id}' vs '{conflicts[0].rule_b_id}' ({conflicts[0].conflict_type})")

    # 3. AI Clarification Proposals and Self-Healing
    print("Testing AI-Assisted Self-Healing Proposals...")
    proposals = get_clarification_proposals()
    assert len(proposals) >= 2, "Expected at least 2 clarification proposals"
    prop = proposals[0]
    assert prop.status == "PENDING_APPROVAL"
    print(f"  ✓ Proposal: '{prop.title}' (Confidence: {prop.confidence_score}%)")
    print(f"  ✓ Est. Dispute Reduction: {prop.estimated_dispute_reduction_pct}%")

    # Apply Proposal
    print("Testing 1-Click Proposal Approval & Self-Healing...")
    apply_res = apply_clarification_proposal(prop.id, admin_user="Chief Compliance Officer")
    assert apply_res["success"] is True
    assert apply_res["proposal"]["status"] == "APPLIED"
    print(f"  ✓ {apply_res['message']}")

    # Check that linked conflict was resolved
    updated_conflicts = get_conflicting_guidelines()
    resolved_linked = [c for c in updated_conflicts if c.id == prop.conflict_id]
    if resolved_linked:
        assert resolved_linked[0].status == "RESOLVED"
        print(f"  ✓ Linked Conflict {resolved_linked[0].id} resolved automatically!")

    # Rollback Proposal
    print("Testing Governance Rollback Safety Mechanism...")
    rollback_res = rollback_clarification_proposal(prop.id, admin_user="Chief Compliance Officer")
    assert rollback_res["success"] is True
    assert rollback_res["proposal"]["status"] == "ROLLED_BACK"
    print(f"  ✓ {rollback_res['message']}")

    # 4. Record Live Dispute Event
    print("Testing Live Dispute Event Submission...")
    disp = record_rule_dispute(
        rule_id="RULE-TONE-01",
        rule_name="Celebratory & Empowering Voice Directive",
        category="Tone & Voice",
        reason="Creator testing live dispute filing during incident announcement",
        user_role="Content Creator"
    )
    assert disp.id.startswith("disp-")
    print(f"  ✓ Live Dispute Recorded: {disp.id} for rule {disp.rule_id}")

    # 5. Governance Velocity & Performance Metrics
    print("Testing Governance Velocity & Performance Metrics...")
    metrics = get_governance_metrics()
    assert 50 <= metrics.overall_health_score <= 100
    assert metrics.mean_time_to_approval_hours == 3.2
    assert metrics.mtta_reduction_pct > 90.0
    print(f"  ✓ Guideline Health Score: {metrics.overall_health_score}/100")
    print(f"  ✓ MTTA: {metrics.mean_time_to_approval_hours} hrs ({metrics.mtta_reduction_pct}% faster)")
    print(f"  ✓ Total Active Rules: {metrics.total_active_rules} | Healthy: {metrics.healthy_rules_count}")
    print("========================================")
    print(" ALL PILLAR 3 GOVERNANCE TESTS PASSED!  ")
    print("========================================")

if __name__ == "__main__":
    test_governance_health_suite()
