import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.api.endpoints import (
    health_check, get_visual_palette, get_visual_samples, inspect_visual_endpoint,
    scan_and_redact_endpoint, restore_privacy_endpoint, get_privacy_ledger,
    get_health_metrics_endpoint, get_disputes_endpoint, create_dispute_endpoint,
    get_conflicts_endpoint, get_proposals_endpoint, apply_proposal_endpoint, rollback_proposal_endpoint,
    VisualInspectRequest, PrivacyScanRequest, PrivacyRestoreRequest, DisputeCreateRequest
)

def test_round3_endpoints_direct():
    print("========================================")
    print(" TESTING ALL ROUND 3 REST API ENDPOINTS ")
    print("========================================")
    
    # 1. Health & Round 3 Commitments
    h = health_check()
    assert h["status"] == "healthy"
    print(f"  ✓ /api/health: {h['status']}")

    # 2. Visual Palette & Samples
    palette_data = get_visual_palette()
    assert len(palette_data["brand_palette"]) >= 5
    print(f"  ✓ /api/visual/palette: {len(palette_data['brand_palette'])} brand swatches")

    samples_data = get_visual_samples()
    samples = samples_data["samples"]
    assert len(samples) >= 3
    print(f"  ✓ /api/visual/samples: {len(samples)} preloaded synthetic assets")

    # 3. Visual Inspection with base64
    sample_b64 = samples[0]["image_data"]
    vis_data = inspect_visual_endpoint(VisualInspectRequest(
        image_base64=sample_b64,
        filename="launch_banner.png",
        asset_type="banner"
    ))
    assert vis_data["overall_visual_score"] >= 80
    print(f"  ✓ /api/visual/inspect: Score={vis_data['overall_visual_score']}, Status={vis_data['clearance_status']}")
    print(f"    - Extracted Colors: {len(vis_data['extracted_dominant_colors'])}")
    print(f"    - WCAG Status: {vis_data['wcag_accessibility']['status']}")

    # 4. Privacy Shield Scan & Redact
    raw_memo = (
        "Internal release memo: Contact CTO Dr. Sarah Jenkins at s.jenkins@apexpay.com or call +1 (555) 019-2834. "
        "Secret credentials sk_test_99887766554433221100aabbcc must never be shared outside 10.0.4.12. "
        "Q3 revenue reached $48.5M ARR with customer vault 4111-2222-3333-4444."
    )
    priv_data = scan_and_redact_endpoint(PrivacyScanRequest(
        text=raw_memo,
        air_gapped_mode=True
    ))
    scan_id = priv_data["scan_result"]["scan_id"]
    redacted_text = priv_data["scan_result"]["redacted_text"]
    assert priv_data["scan_result"]["total_redactions"] >= 5
    print(f"  ✓ /api/privacy/scan-redact: {priv_data['scan_result']['total_redactions']} redactions detected")
    print(f"    - SHA-256 Ledger Entry: {priv_data['disclosure_entry']['id']}")

    # 5. Privacy Reversible Restore
    rest_data = restore_privacy_endpoint(PrivacyRestoreRequest(
        scan_id=scan_id,
        redacted_text=redacted_text
    ))
    assert rest_data["restored_text"] == raw_memo
    print("  ✓ /api/privacy/restore: Exact 100% reversible vault recovery")

    # 6. Privacy Disclosure Ledger
    ledg_data = get_privacy_ledger(limit=10)
    assert len(ledg_data["ledger"]) >= 1
    print(f"  ✓ /api/privacy/ledger: {len(ledg_data['ledger'])} entries retrieved")

    # 7. Guideline Health & Governance Metrics
    gov_data = get_health_metrics_endpoint()
    assert gov_data["overall_health_score"] >= 50
    print(f"  ✓ /api/governance/health-metrics: Health Score={gov_data['overall_health_score']}, MTTA={gov_data['mean_time_to_approval_hours']}h")

    # 8. Rule Dispute Leaderboard
    disp_data = get_disputes_endpoint()
    assert len(disp_data["dispute_analytics"]) >= 4
    print(f"  ✓ /api/governance/disputes: {len(disp_data['dispute_analytics'])} rules analyzed for friction")

    # 9. Policy Conflicts & Contradictions
    conf_data = get_conflicts_endpoint()
    assert len(conf_data["conflicts"]) >= 3
    print(f"  ✓ /api/governance/conflicts: {len(conf_data['conflicts'])} policy collisions detected")

    # 10. AI Clarification Proposals & 1-Click Self-Healing
    prop_data = get_proposals_endpoint()
    assert len(prop_data["proposals"]) >= 1
    target_prop_id = prop_data["proposals"][0]["id"]
    print(f"  ✓ /api/governance/proposals: {len(prop_data['proposals'])} self-healing proposals ready")

    # 1-Click Apply
    apply_res = apply_proposal_endpoint(target_prop_id, admin_user="Chief Compliance Officer")
    assert apply_res["success"] is True
    print(f"  ✓ /api/governance/proposals/apply: {apply_res['message']}")

    # 1-Click Rollback
    rb_res = rollback_proposal_endpoint(target_prop_id, admin_user="Chief Compliance Officer")
    assert rb_res["success"] is True
    print(f"  ✓ /api/governance/proposals/rollback: {rb_res['message']}")

    print("========================================")
    print(" ALL 10 REST API ENDPOINTS FULLY VERIFIED! ")
    print("========================================")

if __name__ == "__main__":
    test_round3_endpoints_direct()
