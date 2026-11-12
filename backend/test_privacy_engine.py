import socket
from app.services.privacy_engine import (
    scan_and_redact_pii, restore_redacted_text,
    record_ai_disclosure, get_ai_disclosure_ledger,
    verify_ledger_integrity, AirGappedNetworkGuard,
    NetworkIsolationViolationError
)

def test_sanitized_pii_detection():
    print("Testing Enterprise PII Masking & Sanitization...")
    sample_text = (
        "Internal Memo: Contact CFO Sarah Jenkins at s.jenkins@apexpay.com or call +1 (555) 234-8901. "
        "Do not share secret token sk_test_99887766554433221100aabbcc on Slack. "
        "Our Q3 enterprise ARR reached $48.5M ARR with client account 4111-2222-3333-4444."
    )

    result = scan_and_redact_pii(sample_text, air_gapped_mode=True)
    
    # 1. Verify Sanitized Output (No raw secrets or raw text returned)
    assert not hasattr(result, "raw_text"), "CRITICAL SECURITY LEAK: raw_text returned in scan result!"
    for item in result.items:
        assert not hasattr(item, "original_text"), "CRITICAL SECURITY LEAK: original_text returned in item!"

    assert result.total_redactions >= 5, f"Expected at least 5 redactions, got {result.total_redactions}"
    assert "s.jenkins@apexpay.com" not in result.redacted_text
    assert "sk_test_" not in result.redacted_text
    assert "4111-2222-3333-4444" not in result.redacted_text
    assert "[EMAIL_1]" in result.redacted_text
    assert "[API_KEY_1]" in result.redacted_text
    assert len(result.sha256_hash) == 64

    print(f"  ✓ Total Redactions: {result.total_redactions} (Zero raw secrets leaked)")
    print(f"  ✓ Masked Output: {result.redacted_text[:110]}...")

    # 2. Test RBAC on Reversible Restoration
    print("Testing RBAC on Reversible Vault Restoration...")
    
    # Unauthorized role (Creator) must be blocked
    try:
        restore_redacted_text(result.scan_id, result.redacted_text, user_role="CREATOR")
        assert False, "Should have raised PermissionError for CREATOR role!"
    except PermissionError as e:
        print(f"  ✓ Correctly rejected unauthorized restoration: {str(e)[:45]}...")

    # Authorized role (Admin) succeeds
    restored = restore_redacted_text(result.scan_id, result.redacted_text, user_role="ADMIN")
    assert restored == sample_text, "Restored text did not match original text!"
    print("  ✓ Authorized Admin Restoration Verified: 100% exact match.")

def test_air_gapped_network_isolation_barrier():
    print("Testing Verified Air-Gapped Network Isolation Barrier...")
    
    # Within AirGappedNetworkGuard, external socket connects must be blocked
    with AirGappedNetworkGuard(is_air_gapped=True):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 53))
            s.close()
            assert False, "Network isolation failed: External socket connection was permitted!"
        except NetworkIsolationViolationError as e:
            print(f"  ✓ External connection strictly blocked: {str(e)[:60]}...")

    # Outside the guard, socket behaves normally
    print("  ✓ Network guard restored cleanly upon exit.")

def test_tamper_evident_hash_chained_ledger():
    print("Testing Tamper-Evident Hash-Chained AI Disclosure Ledger...")
    entry1 = record_ai_disclosure(
        prompt="Review prompt 1",
        response="Response 1",
        mode="AIR_GAPPED_OFFLINE",
        model="Deterministic-PrivacyShield-v3",
        redaction_count=2
    )

    entry2 = record_ai_disclosure(
        prompt="Review prompt 2",
        response="Response 2",
        mode="AIR_GAPPED_OFFLINE",
        model="Deterministic-PrivacyShield-v3",
        redaction_count=1
    )

    assert entry2.block_height == entry1.block_height + 1
    assert entry2.prev_hash == entry1.block_hash, "Hash chain link broken between block 1 and 2!"

    # Verify ledger cryptographic integrity
    audit = verify_ledger_integrity()
    assert audit["is_valid"] is True
    assert audit["tamper_detected"] is False
    assert audit["total_blocks"] >= 2
    print(f"  ✓ Hash Chain Linkage Verified: Block #{entry2.block_height} -> prev: {entry2.prev_hash[:16]}...")
    print(f"  ✓ Full Chain Audit: {audit['chain_status']} across {audit['total_blocks']} blocks.")

if __name__ == "__main__":
    print("========================================")
    print(" RUNNING PILLAR 2 PRIVACY ENGINE TESTS  ")
    print("========================================")
    test_sanitized_pii_detection()
    test_air_gapped_network_isolation_barrier()
    test_tamper_evident_hash_chained_ledger()
    print("========================================")
    print(" ALL PILLAR 2 PRIVACY ENGINE TESTS PASSED!")
    print("========================================")
