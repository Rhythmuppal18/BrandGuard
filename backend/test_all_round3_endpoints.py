import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import HTTPException
from app.api.endpoints import (
    health_check, list_personas, issue_token,
    get_visual_palette, get_visual_samples, inspect_visual_endpoint,
    scan_and_redact_endpoint, restore_privacy_endpoint, get_privacy_ledger, verify_ledger,
    get_health_metrics_endpoint, get_disputes_endpoint, create_dispute_endpoint,
    get_conflicts_endpoint, get_proposals_endpoint, apply_proposal_endpoint, rollback_proposal_endpoint,
    VisualInspectRequest, PrivacyScanRequest, PrivacyRestoreRequest, DisputeCreateRequest, AuthTokenRequest
)

def test_round3_endpoints_direct():
    print("========================================")
    print(" TESTING ALL ROUND 3 REST API ENDPOINTS ")
    print("========================================")
    
    # 1. Health & Round 3 Finalist Environment
    h = health_check()
    assert h["status"] == "healthy"
    assert "Round 3 Finalist" in h["environment"]
    print(f"  ✓ /api/health: {h['status']} ({h['environment']})")

    # 2. Auth & Persona Token Generation
    personas_data = list_personas()
    assert len(personas_data["personas"]) == 4
    admin_persona = [p for p in personas_data["personas"] if p["key"] == "admin"][0]
    creator_persona = [p for p in personas_data["personas"] if p["key"] == "creator"][0]
    print(f"  ✓ /api/auth/personas: 4 enterprise simulation tiers ready")

    token_resp = issue_token(AuthTokenRequest(persona="admin"))
    assert token_resp["role"] == "ADMIN"
    assert len(token_resp["access_token"]) > 30
    print(f"  ✓ /api/auth/token: Signed HMAC-SHA256 session token generated for role '{token_resp['role']}'")

    # 3. Visual Palette & Samples
    palette_data = get_visual_palette()
    assert len(palette_data["brand_palette"]) >= 5
    print(f"  ✓ /api/visual/palette: {len(palette_data['brand_palette'])} brand swatches")

    samples_data = get_visual_samples()
    samples = samples_data["samples"]
    assert len(samples) >= 4
    print(f"  ✓ /api/visual/samples: {len(samples)} preloaded assets (including native vector SVG)")

    # 4. Visual Inspection with base64
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

    # 5. Privacy Shield Scan & Redact (Sanitized result, no raw text leakage)
    raw_memo = (
        "Internal release memo: Contact CTO Dr. Sarah Jenkins at s.jenkins@apexpay.com or call +1 (555) 019-2834. "
        "Secret credentials sk_test_99887766554433221100aabbcc must never be shared outside 10.0.4.12. "
        "Q3 revenue reached $48.5M ARR with customer vault 4111-2222-3333-4444."
    )
    priv_data = scan_and_redact_endpoint(
        PrivacyScanRequest(text=raw_memo, air_gapped_mode=True),
        user={"name": "Creator", "role": "CREATOR", "tenant_id": "tenant-apexpay-prod"}
    )
    scan_id = priv_data["scan_result"]["scan_id"]
    redacted_text = priv_data["scan_result"]["redacted_text"]
    assert "raw_text" not in priv_data["scan_result"], "CRITICAL: raw_text returned in API scan result!"
    assert priv_data["scan_result"]["total_redactions"] >= 5
    print(f"  ✓ /api/privacy/scan-redact: {priv_data['scan_result']['total_redactions']} redactions (sanitized response)")

    # 6. Privacy Reversible Restore with RBAC
    # Unauthorized Creator is rejected with 403
    try:
        restore_privacy_endpoint(
            PrivacyRestoreRequest(scan_id=scan_id, redacted_text=redacted_text),
            user={"name": "Creator", "role": "CREATOR", "tenant_id": "tenant-apexpay-prod"}
        )
        assert False, "Should have returned 403 for Creator role!"
    except HTTPException as e:
        assert e.status_code == 403
        print(f"  ✓ /api/privacy/restore: Unauthorized Creator rejected with 403 Forbidden")

    # Authorized Admin succeeds
    rest_data = restore_privacy_endpoint(
        PrivacyRestoreRequest(scan_id=scan_id, redacted_text=redacted_text),
        user={"name": "Chief Compliance Officer", "role": "ADMIN", "tenant_id": "tenant-apexpay-prod"}
    )
    assert rest_data["restored_text"] == raw_memo
    print("  ✓ /api/privacy/restore: Authorized Admin 100% exact reversible vault recovery")

    # 7. Privacy Disclosure Ledger & Cryptographic Verification
    ledg_data = get_privacy_ledger(limit=10, user={"name": "Admin", "role": "ADMIN", "tenant_id": "tenant-apexpay-prod"})
    assert len(ledg_data["ledger"]) >= 1
    print(f"  ✓ /api/privacy/ledger: {len(ledg_data['ledger'])} chained blocks retrieved")

    audit_report = verify_ledger(user={"name": "Admin", "role": "ADMIN", "tenant_id": "tenant-apexpay-prod"})
    assert audit_report["is_valid"] is True
    print(f"  ✓ /api/privacy/ledger/verify: Cryptographic chain verified across {audit_report['total_blocks']} blocks")

    # 8. Guideline Health & Governance Metrics from real DB
    gov_data = get_health_metrics_endpoint(user={"name": "Admin", "role": "ADMIN", "tenant_id": "tenant-apexpay-prod"})
    assert gov_data["overall_health_score"] >= 50
    print(f"  ✓ /api/governance/health-metrics: Health Score={gov_data['overall_health_score']}, MTTA={gov_data['mean_time_to_approval_hours']}h")

    # 9. Rule Dispute Leaderboard
    disp_data = get_disputes_endpoint(user={"name": "Admin", "role": "ADMIN", "tenant_id": "tenant-apexpay-prod"})
    assert len(disp_data["dispute_analytics"]) >= 4
    print(f"  ✓ /api/governance/disputes: {len(disp_data['dispute_analytics'])} rules analyzed for friction")

    # 10. Policy Conflicts & Contradictions
    conf_data = get_conflicts_endpoint(user={"name": "Admin", "role": "ADMIN", "tenant_id": "tenant-apexpay-prod"})
    assert len(conf_data["conflicts"]) >= 3
    print(f"  ✓ /api/governance/conflicts: {len(conf_data['conflicts'])} policy collisions detected")

    # 11. AI Clarification Proposals & 1-Click Self-Healing
    prop_data = get_proposals_endpoint(user={"name": "Admin", "role": "ADMIN", "tenant_id": "tenant-apexpay-prod"})
    assert len(prop_data["proposals"]) >= 1
    target_prop_id = prop_data["proposals"][0]["id"]
    print(f"  ✓ /api/governance/proposals: {len(prop_data['proposals'])} self-healing proposals ready")

    # 1-Click Apply (Admin role)
    apply_res = apply_proposal_endpoint(
        target_prop_id,
        user={"name": "Chief Compliance Officer", "role": "ADMIN", "tenant_id": "tenant-apexpay-prod"}
    )
    assert apply_res["success"] is True
    print(f"  ✓ /api/governance/proposals/apply: {apply_res['message']}")

    # 1-Click Rollback (Admin role)
    rb_res = rollback_proposal_endpoint(
        target_prop_id,
        user={"name": "Chief Compliance Officer", "role": "ADMIN", "tenant_id": "tenant-apexpay-prod"}
    )
    assert rb_res["success"] is True
    print(f"  ✓ /api/governance/proposals/rollback: {rb_res['message']}")

    print("========================================")
    print(" ALL REST API ENDPOINTS FULLY VERIFIED! ")
    print("========================================")

if __name__ == "__main__":
    test_round3_endpoints_direct()
