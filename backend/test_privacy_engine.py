from app.services.privacy_engine import (
    scan_and_redact_pii, restore_redacted_text,
    record_ai_disclosure, get_ai_disclosure_ledger
)

def test_pii_detection_and_redaction():
    print("Testing Enterprise PII & Secret Redaction...")
    sample_text = (
        "Internal Memo: Contact CFO Sarah Jenkins at s.jenkins@apexpay.com or call +1 (555) 234-8901. "
        "Do not share secret token sk_test_99887766554433221100aabbcc on Slack. "
        "Our Q3 enterprise ARR reached $48.5M ARR with client account 4111-2222-3333-4444."
    )

    result = scan_and_redact_pii(sample_text, air_gapped_mode=True)
    assert result.total_redactions >= 5, f"Expected at least 5 redactions, got {result.total_redactions}"
    assert "s.jenkins@apexpay.com" not in result.redacted_text
    assert "sk_test_" not in result.redacted_text
    assert "4111-2222-3333-4444" not in result.redacted_text
    assert "[EMAIL_1]" in result.redacted_text or "[CONTACT_PII" in result.redacted_text
    assert "[API_KEY_1]" in result.redacted_text
    assert len(result.sha256_hash) == 64

    print(f"  ✓ Total Redactions Detected: {result.total_redactions}")
    print(f"  ✓ Categories Found: {result.categories_found}")
    print(f"  ✓ Masked Preview: {result.redacted_text[:120]}...")

    # Test Reversible Restoration
    restored = restore_redacted_text(result.scan_id, result.redacted_text)
    assert restored == sample_text, "Restored text did not match original raw text!"
    print("  ✓ Reversible Restoration Verified: 100% exact match.")

def test_ai_disclosure_ledger():
    print("Testing Cryptographic AI Disclosure Ledger...")
    entry = record_ai_disclosure(
        prompt="Review confidential financial release",
        response="Detected 3 policy infractions",
        mode="AIR_GAPPED_OFFLINE",
        model="Deterministic-Engine-v2",
        redaction_count=4,
        categories=["API_CREDENTIAL", "CONTACT_PII"],
        latency_ms=0.18
    )

    assert entry.id.startswith("ledg-")
    assert len(entry.prompt_hash) == 64
    assert len(entry.response_hash) == 64
    assert entry.status == "VERIFIED_TAMPER_EVIDENT"

    ledger = get_ai_disclosure_ledger(limit=10)
    assert len(ledger) >= 1
    assert ledger[0]["id"] == entry.id
    print(f"  ✓ Recorded Ledger Entry: {entry.id}")
    print(f"  ✓ Prompt SHA-256: {entry.prompt_hash[:16]}... Response SHA-256: {entry.response_hash[:16]}...")

if __name__ == "__main__":
    print("========================================")
    print(" RUNNING PILLAR 2 PRIVACY ENGINE TESTS  ")
    print("========================================")
    test_pii_detection_and_redaction()
    test_ai_disclosure_ledger()
    print("========================================")
    print(" ALL PILLAR 2 PRIVACY ENGINE TESTS PASSED!")
    print("========================================")
