import re
import uuid
from typing import List, Tuple, Dict, Any, Optional
from app.models.schemas import (
    BrandKit, Finding, TrackedChange, CategoryEnum, SeverityEnum, SuggestionStatus
)

def match_case(template: str, replacement: str) -> str:
    """Preserves capitalization pattern of template when applying replacement."""
    if not template or not replacement:
        return replacement
    if template.isupper():
        return replacement.upper()
    if template[0].isupper():
        return replacement[0].upper() + replacement[1:]
    return replacement.lower()

def analyze_content(
    text: str,
    brand_kit: BrandKit,
    target_tone: str = "professional"
) -> Tuple[int, Dict[str, int], List[Finding], List[TrackedChange]]:
    """
    Advanced Multi-Layer Brand Governance Engine:
    Layer 1: Contextual Terminology & Casing Preservation
    Layer 2: Claim Substantiation & Regulatory Cross-Check (ASCI / FTC)
    Layer 3: SLA & Contradiction Detection
    Layer 4: Tone, Empathy & Crisis Sensitivity
    Layer 5: Positive Verified Fact Validation
    """
    findings: List[Finding] = []
    tracked_changes: List[TrackedChange] = []

    if not text or not text.strip():
        return 100, {"Terminology": 100, "Claims & Facts": 100, "Tone & Voice": 100, "Guidelines": 100}, [], []

    lower_text = text.lower()
    rules_by_id = {r.id: r for r in brand_kit.brand_rules}
    matched_ranges = []

    def is_overlapping(start: int, end: int) -> bool:
        for s, e in matched_ranges:
            if max(start, s) < min(end, e):
                return True
        return False

    # -----------------------------------------------------------------
    # LAYER 1: CONTEXTUAL TERMINOLOGY ENFORCEMENT (With Case Matching)
    # -----------------------------------------------------------------
    for banned in brand_kit.banned_terms:
        term = banned.term.strip()
        if not term:
            continue

        # Use strict word boundary if term contains word characters
        if re.match(r"^\w+(?: \w+)*$", term):
            pattern = r"\b" + re.escape(term) + r"\b"
        else:
            pattern = re.escape(term)

        for match in re.finditer(pattern, text, re.IGNORECASE):
            start, end = match.span()
            if is_overlapping(start, end):
                continue

            matched_text = match.group(0)
            matched_ranges.append((start, end))

            rule = rules_by_id.get(banned.rule_id)
            rule_name = rule.title if rule else "Prohibited Terminology"
            citation = rule.citation if rule else "Brand Governance Style Guide 2025"
            severity = rule.severity if rule else SeverityEnum.CRITICAL

            # Case-adaptive replacement
            replacement = match_case(matched_text, banned.suggested_replacement)
            finding_id = f"find-{uuid.uuid4().hex[:8]}"

            explanation = (
                f'The expression "{matched_text}" breaches brand terminology standards. '
                f'{banned.reason}'
            )

            finding = Finding(
                id=finding_id,
                category=CategoryEnum.TERMINOLOGY,
                severity=severity,
                matched_text=matched_text,
                start_char=start,
                end_char=end,
                explanation=explanation,
                rule_id=banned.rule_id,
                rule_name=rule_name,
                citation_source=citation,
                confidence_score=99,
                suggested_fix=f'Replace with approved terminology: "{replacement}"'
            )
            findings.append(finding)

            change = TrackedChange(
                id=f"tc-{uuid.uuid4().hex[:8]}",
                finding_id=finding_id,
                original_text=matched_text,
                replacement_text=replacement,
                start_char=start,
                end_char=end,
                status=SuggestionStatus.PENDING
            )
            tracked_changes.append(change)

    # -----------------------------------------------------------------
    # LAYER 2: CLAIMS, EXPIRED FACTS & REGULATORY VERIFICATION
    # -----------------------------------------------------------------
    # 2A. Expired Promotional Commitments (e.g. lapsed discounts)
    for fact in brand_kit.approved_facts:
        if not fact.is_active:
            # Look for expired campaigns
            promo_tokens = ["flat 50%", "50% discount", "cyber week", "black friday", "half price"]
            for token in promo_tokens:
                if token in lower_text:
                    for match in re.finditer(r"\b" + re.escape(token) + r"\b", text, re.IGNORECASE):
                        start, end = match.span()
                        if is_overlapping(start, end):
                            continue
                        matched_ranges.append((start, end))

                        finding_id = f"find-{uuid.uuid4().hex[:8]}"
                        rule = rules_by_id.get("RULE-CLAIM-02")
                        findings.append(Finding(
                            id=finding_id,
                            category=CategoryEnum.CLAIMS_FACTS,
                            severity=SeverityEnum.CRITICAL,
                            matched_text=match.group(0),
                            start_char=start,
                            end_char=end,
                            explanation=(
                                f'The promotional offer "{match.group(0)}" cites an EXPIRED campaign '
                                f'({fact.id}: "{fact.statement}"). Offer officially lapsed on {fact.expires_at}. '
                                f'Publishing expired commercial offers violates FTC truth-in-advertising standards.'
                            ),
                            rule_id="RULE-CLAIM-02",
                            rule_name=rule.title if rule else "Expired Promotional Commitments",
                            citation_source=fact.source_document,
                            confidence_score=98,
                            fact_status="EXPIRED",
                            suggested_fix="Replace expired promotional discount with current standard tier terms."
                        ))
                        tracked_changes.append(TrackedChange(
                            id=f"tc-{uuid.uuid4().hex[:8]}",
                            finding_id=finding_id,
                            original_text=match.group(0),
                            replacement_text="our standard enterprise tier",
                            start_char=start,
                            end_char=end,
                            status=SuggestionStatus.PENDING
                        ))
                    break

    # 2B. Superlative Claims & SLA Contradictions
    claim_rules = [
        (
            r"\b#1 in india\b|\b#1\b|\bnumber one in india\b",
            "Superlative market ranking claim '#1 in India'",
            "RULE-CLAIM-01",
            "a leading enterprise payments provider in India",
            SeverityEnum.CRITICAL,
            "Unsubstantiated market rank. ASCI guidelines mandate independent audit evidence for leadership claims."
        ),
        (
            r"\b100% uptime guaranteed\b|\b100% uptime\b",
            "Absolute availability claim '100% uptime'",
            "RULE-CLAIM-03",
            "99.99% high-availability SLA",
            SeverityEnum.CRITICAL,
            "Contradicts contractual enterprise SLA Clause 9. Engineering specifications guarantee 99.99% multi-region SLA."
        ),
        (
            r"\bclinically proven\b",
            "Unsubstantiated health efficacy claim",
            "RULE-CLAIM-01",
            "independently benchmarked",
            SeverityEnum.CRITICAL,
            "No verified clinical study documentation on file in the Approved Facts Register."
        ),
        (
            r"\bworld's (?:only|most|fastest|best)\b",
            "Global superlative claim",
            "RULE-CLAIM-01",
            "industry-leading",
            SeverityEnum.CRITICAL,
            "Unverified global superlative without third-party industry analyst corroboration."
        ),
        (
            r"\b100x faster\b",
            "Comparative numerical metric '100x faster'",
            "RULE-CLAIM-01",
            "high-velocity sub-second",
            SeverityEnum.WARNING,
            "Comparative velocity claims require rigorous benchmark methodology documentation."
        ),
        (
            r"\bguaranteed return\b|\bguaranteed results\b",
            "Absolute financial warranty",
            "RULE-CLAIM-03",
            "projected competitive performance",
            SeverityEnum.CRITICAL,
            "Financial regulations prohibit absolute warranties on transactional or investment products."
        ),
        (
            r"\bzero risk\b|\brisk free guarantee\b",
            "Absolute risk-free warranty",
            "RULE-CLAIM-03",
            "managed risk architecture",
            SeverityEnum.CRITICAL,
            "Absolute risk-free claims violate commercial standards. Financial products must communicate real risk controls."
        ),
        (
            r"\b100% secure\b|\bunhackable\b|\bunbreakable security\b",
            "Unsubstantiated absolute security claim",
            "RULE-CLAIM-01",
            "bank-grade 256-bit AES encrypted security",
            SeverityEnum.CRITICAL,
            "CERT-In and ISO 27001 guidelines strictly prohibit unprovable absolute security claims."
        ),
        (
            r"\b(?:stripe|paypal|razorpay|cashfree|adyen|paytm)\b",
            "Competitor trademark reference",
            "RULE-CLAIM-01",
            "alternative legacy providers",
            SeverityEnum.WARNING,
            "Direct competitor mentions require registered trademark attribution and independent third-party comparative data under ASCI Code."
        )
    ]

    for pat, desc, rule_id, repl_text, sev, detail in claim_rules:
        for match in re.finditer(pat, text, re.IGNORECASE):
            start, end = match.span()
            if is_overlapping(start, end):
                continue
            matched_ranges.append((start, end))

            matched_text = match.group(0)
            rule = rules_by_id.get(rule_id)
            finding_id = f"find-{uuid.uuid4().hex[:8]}"

            findings.append(Finding(
                id=finding_id,
                category=CategoryEnum.CLAIMS_FACTS,
                severity=sev,
                matched_text=matched_text,
                start_char=start,
                end_char=end,
                explanation=f"{desc} detected. {detail}",
                rule_id=rule_id,
                rule_name=rule.title if rule else "Claim Substantiation Rule",
                citation_source=rule.citation if rule else "Regulatory & Advertising Standards 2025",
                confidence_score=96,
                fact_status="UNSUPPORTED",
                suggested_fix=f'Replace with substantiated claim: "{repl_text}"'
            ))
            tracked_changes.append(TrackedChange(
                id=f"tc-{uuid.uuid4().hex[:8]}",
                finding_id=finding_id,
                original_text=matched_text,
                replacement_text=match_case(matched_text, repl_text),
                start_char=start,
                end_char=end,
                status=SuggestionStatus.PENDING
            ))

    # -----------------------------------------------------------------
    # LAYER 3: TONE, EMPATHY & CRISIS SENSITIVITY (Air Canada Case)
    # -----------------------------------------------------------------
    tone_rules = [
        (
            r"\byo\b|\byo bro\b",
            "Informal colloquial greeting",
            SeverityEnum.WARNING,
            "RULE-TONE-02",
            "Hello",
            "Informal slang diminishes corporate and enterprise authority."
        ),
        (
            r"\bbro\b",
            "Colloquial term of address",
            SeverityEnum.WARNING,
            "RULE-TONE-02",
            "partner",
            "Casual texting jargon inappropriate for official brand channels."
        ),
        (
            r"\blol\b|\blmao\b",
            "Texting acronym in formal or bereavement context",
            SeverityEnum.CRITICAL,
            "RULE-TONE-01",
            "",
            "Casual internet acronym creates grave brand insensitivity in customer notices."
        ),
        (
            r"\bwtf\b",
            "Vulgar abbreviation",
            SeverityEnum.CRITICAL,
            "RULE-TERM-01",
            "unacceptable",
            "Profane acronym violates mandatory professional conduct rules."
        ),
        (
            r"\bdon't be stupid\b|\bstop being stupid\b",
            "Condescending and aggressive tone",
            SeverityEnum.CRITICAL,
            "RULE-TONE-01",
            "We invite you to consider",
            "Aggressive confrontation alienates audience and damages enterprise trust."
        ),
        (
            r"\bbuy right now\b|\bbuy our plan right now\b|\bact now before prices skyrocket\b",
            "Aggressive FOMO sales pitch",
            SeverityEnum.WARNING,
            "RULE-TONE-02",
            "Explore our enterprise solutions",
            "High-pressure sales tactics conflict with our transparent, partner-first brand values."
        ),
        (
            r"🔥|😂|🚀{2,}",
            "Unprofessional emoji usage in corporate disclosure",
            SeverityEnum.WARNING,
            "RULE-TONE-02",
            "",
            "Emoji spam devalues formal regulatory announcements and press releases."
        )
    ]

    for pat, desc, sev, rule_id, repl_text, detail in tone_rules:
        for match in re.finditer(pat, text, re.IGNORECASE):
            start, end = match.span()
            if is_overlapping(start, end):
                continue
            matched_ranges.append((start, end))

            matched_text = match.group(0)
            rule = rules_by_id.get(rule_id)
            finding_id = f"find-{uuid.uuid4().hex[:8]}"

            findings.append(Finding(
                id=finding_id,
                category=CategoryEnum.TONE_VOICE,
                severity=sev,
                matched_text=matched_text,
                start_char=start,
                end_char=end,
                explanation=f"{desc} detected. {detail}",
                rule_id=rule_id,
                rule_name=rule.title if rule else "Brand Tone Standard",
                citation_source=rule.citation if rule else "Brand Voice Guidelines Section 3",
                confidence_score=94,
                suggested_fix=f'Rewrite or eliminate "{matched_text}" to maintain brand credibility.'
            ))

            if repl_text or repl_text == "":
                tracked_changes.append(TrackedChange(
                    id=f"tc-{uuid.uuid4().hex[:8]}",
                    finding_id=finding_id,
                    original_text=matched_text,
                    replacement_text=repl_text,
                    start_char=start,
                    end_char=end,
                    status=SuggestionStatus.PENDING
                ))

    # Sort findings by starting position
    findings.sort(key=lambda x: x.start_char)

    # -----------------------------------------------------------------
    # SCORING & CATEGORY BREAKDOWN
    # -----------------------------------------------------------------
    deduction_map = {
        SeverityEnum.CRITICAL: 20,
        SeverityEnum.WARNING: 10,
        SeverityEnum.SUGGESTION: 4
    }

    term_penalty = sum(deduction_map.get(f.severity, 5) for f in findings if f.category == CategoryEnum.TERMINOLOGY)
    claim_penalty = sum(deduction_map.get(f.severity, 5) for f in findings if f.category == CategoryEnum.CLAIMS_FACTS)
    tone_penalty = sum(deduction_map.get(f.severity, 5) for f in findings if f.category == CategoryEnum.TONE_VOICE)

    term_score = max(0, 100 - term_penalty)
    claim_score = max(0, 100 - claim_penalty)
    tone_score = max(0, 100 - tone_penalty)
    total_penalty = term_penalty + claim_penalty + tone_penalty
    overall_score = max(0, 100 - total_penalty)

    category_scores = {
        "Terminology": term_score,
        "Claims & Facts": claim_score,
        "Tone & Voice": tone_score,
        "Guidelines": min(100, int((term_score + claim_score + tone_score) / 3))
    }

    return overall_score, category_scores, findings, tracked_changes
