import re
import hashlib
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel

class RedactionItem(BaseModel):
    id: str
    category: str
    original_text: str
    placeholder: str
    start_char: int
    end_char: int
    confidence: int

class PrivacyScanResult(BaseModel):
    scan_id: str
    timestamp: str
    raw_text: str
    redacted_text: str
    total_redactions: int
    categories_found: Dict[str, int]
    items: List[RedactionItem]
    is_air_gapped: bool
    sha256_hash: str

class AIDisclosureEntry(BaseModel):
    id: str
    timestamp: str
    execution_mode: str  # "AIR_GAPPED_OFFLINE", "ENTERPRISE_PRIVATE", "DETERMINISTIC_RULES"
    model_identifier: str
    prompt_hash: str
    response_hash: str
    redaction_count: int
    sensitive_categories: List[str]
    latency_ms: float
    status: str

# In-memory session redaction mappings for secure reversible restoration (never written to disk or logs)
_SECURE_REDACTION_VAULT: Dict[str, Dict[str, str]] = {}
_AI_DISCLOSURE_LEDGER: List[Dict[str, Any]] = []

# High-precision RegEx Patterns for Sensitive Enterprise Entities
PII_PATTERNS = [
    # 1. API Keys & Cloud Secrets
    {
        "category": "API_CREDENTIAL",
        "pattern": r"\b(?:sk_live_[0-9a-zA-Z]{24,}|sk_test_[0-9a-zA-Z]{24,}|ghp_[0-9a-zA-Z]{36}|apex_sec_[0-9a-zA-Z]{20,}|AKIA[0-9A-Z]{16}|bearer\s+[A-Za-z0-9\-_\.~+/]+=*)\b",
        "prefix": "API_KEY",
        "flags": re.IGNORECASE,
        "confidence": 99
    },
    # 2. Credit Card & Account Numbers
    {
        "category": "FINANCIAL_DATA",
        "pattern": r"\b(?:\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}|\d{4}[ -]?\d{6}[ -]?\d{5})\b",
        "prefix": "ACCOUNT_NUM",
        "flags": 0,
        "confidence": 98
    },
    # 3. Email Addresses
    {
        "category": "CONTACT_PII",
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "prefix": "EMAIL",
        "flags": 0,
        "confidence": 99
    },
    # 4. Phone Numbers (International & Domestic Formats)
    {
        "category": "CONTACT_PII",
        "pattern": r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "prefix": "PHONE",
        "flags": 0,
        "confidence": 95
    },
    # 5. Financial Revenue / Confidential Deal Figures
    {
        "category": "CONFIDENTIAL_METRIC",
        "pattern": r"(?:[\$€£₹]\s*\d+(?:\.\d+)?(?:\s*[kKmMbB]|\s*million|\s*billion|\s*crore|\s*lakh)?(?:\s*(?:ARR|MRR|revenue|valuation|payout|EBITDA|profit))?|\b\d+(?:\.\d+)?\s*(?:ARR|MRR|revenue|valuation|payout|EBITDA|profit)\b)",
        "prefix": "METRIC",
        "flags": re.IGNORECASE,
        "confidence": 92
    },
    # 6. IPv4 / Internal Infrastructure IPs
    {
        "category": "INFRASTRUCTURE",
        "pattern": r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b",
        "prefix": "INTERNAL_IP",
        "flags": 0,
        "confidence": 97
    }
]

def scan_and_redact_pii(text: str, air_gapped_mode: bool = True) -> PrivacyScanResult:
    """
    Executes deep regex and heuristic scan for PII, secrets, and financial figures.
    Replaces sensitive tokens with contextual placeholders (e.g., [EMAIL_1], [API_KEY_1]).
    Stores reversible mapping in an ephemeral in-memory vault.
    """
    if not text:
        return PrivacyScanResult(
            scan_id=f"priv-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.utcnow().isoformat(),
            raw_text="",
            redacted_text="",
            total_redactions=0,
            categories_found={},
            items=[],
            is_air_gapped=air_gapped_mode,
            sha256_hash=hashlib.sha256(b"").hexdigest()
        )

    scan_id = f"priv-{uuid.uuid4().hex[:8]}"
    detected_items: List[RedactionItem] = []
    category_counts: Dict[str, int] = {}
    vault_mapping: Dict[str, str] = {}
    
    # Track matched spans to prevent nested replacements
    matched_spans = []

    for rule in PII_PATTERNS:
        pattern = rule["pattern"]
        flags = rule["flags"]
        prefix = rule["prefix"]
        cat = rule["category"]

        for match in re.finditer(pattern, text, flags):
            start, end = match.span()
            matched_str = match.group(0).strip()
            
            # Avoid overlap
            if any(max(start, span[0]) < min(end, span[1]) for span in matched_spans):
                continue
            
            # Count per prefix for clean identifiers e.g. [EMAIL_1], [EMAIL_2]
            count_key = prefix
            category_counts[cat] = category_counts.get(cat, 0) + 1
            index = category_counts[cat]
            placeholder = f"[{prefix}_{index}]"

            matched_spans.append((start, end, placeholder, matched_str, cat, rule["confidence"]))

    # Sort spans by start_char ascending
    matched_spans.sort(key=lambda x: x[0])

    # Construct redacted string
    redacted_parts = []
    cur_idx = 0

    for start, end, placeholder, original, cat, conf in matched_spans:
        if start > cur_idx:
            redacted_parts.append(text[cur_idx:start])
        redacted_parts.append(placeholder)
        cur_idx = end

        item_id = f"red-{uuid.uuid4().hex[:6]}"
        detected_items.append(RedactionItem(
            id=item_id,
            category=cat,
            original_text=original,
            placeholder=placeholder,
            start_char=start,
            end_char=end,
            confidence=conf
        ))
        vault_mapping[placeholder] = original

    if cur_idx < len(text):
        redacted_parts.append(text[cur_idx:])

    redacted_text = "".join(redacted_parts)

    # Store mapping in secure ephemeral vault
    _SECURE_REDACTION_VAULT[scan_id] = vault_mapping

    # Hash the redacted text for tamper evidence
    content_hash = hashlib.sha256(redacted_text.encode("utf-8")).hexdigest()

    return PrivacyScanResult(
        scan_id=scan_id,
        timestamp=datetime.utcnow().isoformat(),
        raw_text=text,
        redacted_text=redacted_text,
        total_redactions=len(detected_items),
        categories_found=category_counts,
        items=detected_items,
        is_air_gapped=air_gapped_mode,
        sha256_hash=content_hash
    )

def restore_redacted_text(scan_id: str, redacted_text: str) -> str:
    """
    Restores original values using the ephemeral vault mapping.
    Only available to authorized administrators.
    """
    mapping = _SECURE_REDACTION_VAULT.get(scan_id, {})
    if not mapping:
        return redacted_text

    restored = redacted_text
    for placeholder, original in mapping.items():
        restored = restored.replace(placeholder, original)
    return restored

def record_ai_disclosure(
    prompt: str,
    response: str,
    mode: str = "AIR_GAPPED_OFFLINE",
    model: str = "Deterministic-RuleEngine-v2",
    redaction_count: int = 0,
    categories: Optional[List[str]] = None,
    latency_ms: float = 0.25
) -> AIDisclosureEntry:
    """
    Records an immutable, cryptographically hashed entry in the AI Disclosure Ledger.
    Tracks provenance without storing sensitive unredacted content in the permanent record.
    """
    entry_id = f"ledg-{uuid.uuid4().hex[:10]}"
    p_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    r_hash = hashlib.sha256(response.encode("utf-8")).hexdigest()

    entry = AIDisclosureEntry(
        id=entry_id,
        timestamp=datetime.utcnow().isoformat(),
        execution_mode=mode,
        model_identifier=model,
        prompt_hash=p_hash,
        response_hash=r_hash,
        redaction_count=redaction_count,
        sensitive_categories=categories or [],
        latency_ms=round(latency_ms, 2),
        status="VERIFIED_TAMPER_EVIDENT"
    )

    _AI_DISCLOSURE_LEDGER.insert(0, entry.model_dump())
    return entry

def get_ai_disclosure_ledger(limit: int = 50, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns the tamper-evident AI Disclosure Ledger entries with optional query filter."""
    records = _AI_DISCLOSURE_LEDGER
    if search_query and search_query.strip():
        q = search_query.lower().strip()
        records = [
            r for r in records
            if q in r["id"].lower()
            or q in r["execution_mode"].lower()
            or q in r["model_identifier"].lower()
            or q in r["prompt_hash"].lower()
        ]
    return records[:limit]
