from typing import List, Dict, Any
from app.models.schemas import (
    BrandKit, ApprovedFact, BannedTerm, PreferredTerm, BrandRule,
    CategoryEnum, SeverityEnum, BenchmarkItem
)

def get_default_brand_kit() -> BrandKit:
    approved_facts = [
        ApprovedFact(
            id="FACT-01",
            claim_key="transaction_volume",
            statement="ApexPay processes over 50 million transactions monthly with 99.99% high-availability SLA.",
            source_document="ApexPay FY25 Audited Performance Report, Pg. 14",
            verified_by="VP of Engineering (Dr. A. Sharma)",
            valid_from="2025-01-01",
            expires_at="2026-12-31",
            is_active=True
        ),
        ApprovedFact(
            id="FACT-02",
            claim_key="onboarding_trial",
            statement="Zero transaction processing fees for the first 30 days on Starter tier.",
            source_document="Global Pricing Charter v4.1, Schedule B",
            verified_by="Head of Commercial Pricing",
            valid_from="2025-06-01",
            expires_at="2026-12-31",
            is_active=True
        ),
        ApprovedFact(
            id="FACT-03",
            claim_key="compliance_cert",
            statement="Certified PCI-DSS Level 1 Service Provider and ISO/IEC 27001:2022 audited.",
            source_document="Bureau Veritas Audit Certificate #IS-99201",
            verified_by="Chief Compliance Officer",
            valid_from="2024-11-01",
            expires_at="2026-11-30",
            is_active=True
        ),
        ApprovedFact(
            id="FACT-04",
            claim_key="support_tier",
            statement="24/7 dedicated member concierge support with sub-15-minute response SLA on Enterprise tier.",
            source_document="Customer Experience SLA Agreement 2025",
            verified_by="Director of Customer Success",
            valid_from="2025-01-01",
            expires_at="2026-12-31",
            is_active=True
        ),
        ApprovedFact(
            id="FACT-05",
            claim_key="black_friday_promo",
            statement="Flat 50% discount on Enterprise annual plan during Cyber Week.",
            source_document="Marketing Campaign Plan Q4-2024 (EXPIRED)",
            verified_by="Marketing Operations",
            valid_from="2024-11-15",
            expires_at="2024-12-01",
            is_active=False
        ),
        ApprovedFact(
            id="FACT-06",
            claim_key="cross_border_presence",
            statement="Licensed and operating cross-border settlement rails in 28 countries.",
            source_document="Treasury & Regulatory Filing Schedule 2025",
            verified_by="Legal Counsel",
            valid_from="2025-01-01",
            expires_at="2026-12-31",
            is_active=True
        )
    ]

    brand_rules = [
        BrandRule(
            id="RULE-TERM-01",
            category=CategoryEnum.TERMINOLOGY,
            title="Prohibited Colloquialisms & Banned Vocabulary",
            description="Informal slang, emojis in corporate communication, and non-approved adjectives diminish brand credibility.",
            citation="Brand Style Guide 2025, Section 3.1: Voice Standards",
            severity=SeverityEnum.WARNING
        ),
        BrandRule(
            id="RULE-TERM-02",
            category=CategoryEnum.TERMINOLOGY,
            title="Mandatory Member Nomenclature",
            description="Our clients are partners in an enterprise ecosystem. Refer to them as 'members' or 'partners', never as generic 'customers'.",
            citation="Brand Style Guide 2025, Section 2.4: Brand Terminology",
            severity=SeverityEnum.CRITICAL
        ),
        BrandRule(
            id="RULE-CLAIM-01",
            category=CategoryEnum.CLAIMS_FACTS,
            title="Unverified Superlative Claims",
            description="Claims asserting market leadership, rank ('#1', 'best', 'fastest'), or absolute efficacy must cite an approved active fact.",
            citation="Regulatory & Advertising Policy 2025, Section 4.2 (FTC/ASCI Compliance)",
            severity=SeverityEnum.CRITICAL
        ),
        BrandRule(
            id="RULE-CLAIM-02",
            category=CategoryEnum.CLAIMS_FACTS,
            title="Expired or Stale Promotional Commitments",
            description="Promotional campaigns with expired end dates must never be circulated as active promises.",
            citation="Commercial Legal Policy, Section 6.1: Pricing Integrity",
            severity=SeverityEnum.CRITICAL
        ),
        BrandRule(
            id="RULE-CLAIM-03",
            category=CategoryEnum.CLAIMS_FACTS,
            title="Absolute Availability & Zero-Risk Guarantees",
            description="No system is 100% immune from failure. State the contractual 99.99% high-availability SLA instead of '100% guaranteed uptime' or 'risk-free'.",
            citation="Enterprise SLA Framework, Clause 9",
            severity=SeverityEnum.CRITICAL
        ),
        BrandRule(
            id="RULE-TONE-01",
            category=CategoryEnum.TONE_VOICE,
            title="Empathetic & Solemn Tone for Customer Exceptions",
            description="In bereavement, dispute resolution, or service interruption notices, tone must be respectful, empathetic, and unambiguous.",
            citation="Brand Governance Handbook, Chapter 5: Crisis & Support Communication",
            severity=SeverityEnum.CRITICAL
        ),
        BrandRule(
            id="RULE-TONE-02",
            category=CategoryEnum.TONE_VOICE,
            title="Avoid Aggressive Sales Hyperbole",
            description="Avoid pressure tactics ('act now or lose out', 'unlimited freebies', 'craziest deal').",
            citation="Brand Style Guide 2025, Section 3.3",
            severity=SeverityEnum.WARNING
        )
    ]

    banned_terms = [
        BannedTerm(
            id="BT-01",
            term="customers",
            reason="Violates mandatory member terminology rule.",
            suggested_replacement="members",
            rule_id="RULE-TERM-02"
        ),
        BannedTerm(
            id="BT-02",
            term="cheap",
            reason="Devalues brand perception. Use professional value-driven language.",
            suggested_replacement="cost-effective",
            rule_id="RULE-TERM-01"
        ),
        BannedTerm(
            id="BT-03",
            term="100% uptime guaranteed",
            reason="Unsubstantiated absolute guarantee. Breaches SLA compliance.",
            suggested_replacement="99.99% high-availability SLA",
            rule_id="RULE-CLAIM-03"
        ),
        BannedTerm(
            id="BT-04",
            term="best in india",
            reason="Superlative market rank without regulatory substantiation file.",
            suggested_replacement="recognized leader in Indian digital payments",
            rule_id="RULE-CLAIM-01"
        ),
        BannedTerm(
            id="BT-05",
            term="risk-free",
            reason="Misleading financial guarantee. Financial products carry governance terms.",
            suggested_replacement="enterprise-grade with comprehensive safeguards",
            rule_id="RULE-CLAIM-03"
        ),
        BannedTerm(
            id="BT-06",
            term="hacks",
            reason="Colloquial term implying insecure workarounds.",
            suggested_replacement="best practices",
            rule_id="RULE-TERM-01"
        ),
        BannedTerm(
            id="BT-07",
            term="unlimited refund",
            reason="Unauthorized policy expansion risking legal liability (Air Canada precedent).",
            suggested_replacement="standard refund policy as specified in member agreement",
            rule_id="RULE-TONE-01"
        ),
        BannedTerm(
            id="BT-08",
            term="no questions asked",
            reason="Creates unfulfillable commercial warranty.",
            suggested_replacement="under standard verified return procedures",
            rule_id="RULE-TONE-01"
        )
    ]

    preferred_terms = [
        PreferredTerm(
            id="PT-01",
            preferred="members",
            context="Use when addressing our account holders and community.",
            rule_id="RULE-TERM-02"
        ),
        PreferredTerm(
            id="PT-02",
            preferred="multi-region failover",
            context="Technical resilience architecture reference.",
            rule_id="RULE-CLAIM-03"
        ),
        PreferredTerm(
            id="PT-03",
            preferred="ISO 27001 verified",
            context="Information security positioning.",
            rule_id="RULE-CLAIM-01"
        ),
        PreferredTerm(
            id="PT-04",
            preferred="concierge support",
            context="Premium service tier reference.",
            rule_id="RULE-TERM-01"
        )
    ]

    return BrandKit(
        brand_name="ApexPay Global",
        mission="Secure, transparent enterprise financial infrastructure",
        tone_primary="Professional, precise, customer-first",
        prohibited_tones=["Casual slang", "Overly aggressive sales", "Hyperbolic guarantees", "Condescending"],
        approved_facts=approved_facts,
        brand_rules=brand_rules,
        banned_terms=banned_terms,
        preferred_terms=preferred_terms
    )

def get_preloaded_scenarios() -> List[Dict[str, Any]]:
    return [
        {
            "id": "scenario-1",
            "title": "Marketing Launch Social Post",
            "content_type": "social_post",
            "summary": "Multiple severe violations: banned slang, outdated 50% discount, unsubstantiated #1 rank, and cheap phrasing.",
            "text": "ApexPay is officially the best in India! 🔥 We guarantee 100% uptime guaranteed for all our customers, bro. Get our cheap starter pack with a flat 50% discount on Enterprise annual plan today! No questions asked."
        },
        {
            "id": "scenario-2",
            "title": "Customer Bereavement & Refund Policy Notice",
            "content_type": "support_notice",
            "summary": "Air Canada precedent danger: unapproved unlimited refund promise, robotic dismissals, and incorrect customer terminology.",
            "text": "To all customers filing bereavement fare requests: don't worry lol, our system offers an unlimited refund with no questions asked! Just message support for your risk-free payout."
        },
        {
            "id": "scenario-3",
            "title": "Cloud Infrastructure Press Release",
            "content_type": "press_release",
            "summary": "Technical press release with superlative claims, lacking preferred terminology for resilience.",
            "text": "ApexPay announced today that it has built the world's most bulletproof financial cloud. We deliver 100% uptime guaranteed, beating every competitor. Our customers can now execute high speed hacks to maximize yield."
        },
        {
            "id": "scenario-4",
            "title": "Partner Ecosystem Email Blast",
            "content_type": "marketing_email",
            "summary": "Informal tone mismatch, missing member terminology, and casual slang.",
            "text": "Hey yo! Check out these cool growth hacks for your platform. We give our customers cheap onboarding and guaranteed 100% uptime. See you on the other side!"
        },
        {
            "id": "scenario-5",
            "title": "Compliant Quarterly Governance Release",
            "content_type": "blog",
            "summary": "100% brand compliant sample: uses approved facts, preferred terms, professional tone, and strict SLA references.",
            "text": "ApexPay is proud to announce another record quarter. ApexPay processes over 50 million transactions monthly with 99.99% high-availability SLA. As certified PCI-DSS Level 1 Service Provider and ISO/IEC 27001:2022 audited, we continue to empower our members worldwide with enterprise-grade infrastructure and dedicated concierge support."
        }
    ]

def get_benchmark_dataset() -> List[BenchmarkItem]:
    test_cases = [
        # 1-10: Terminology and slang violations
        BenchmarkItem(
            id="TEST-01",
            title="Banned word 'customers' usage",
            sample_text="All customers are requested to update their tax profiles by Friday.",
            expected_issues_count=1,
            expected_categories=["Terminology"]
        ),
        BenchmarkItem(
            id="TEST-02",
            title="Banned word 'cheap' in pricing",
            sample_text="Our cheap software tiers allow early-stage teams to scale.",
            expected_issues_count=1,
            expected_categories=["Terminology"]
        ),
        BenchmarkItem(
            id="TEST-03",
            title="Casual slang 'yo' and 'bro'",
            sample_text="Yo bro, check out our new transaction gateway update!",
            expected_issues_count=2,
            expected_categories=["Tone & Voice", "Terminology"]
        ),
        BenchmarkItem(
            id="TEST-04",
            title="Slang abbreviation 'lol' in support",
            sample_text="We encountered a minor server reboot lol, but everything is back up.",
            expected_issues_count=1,
            expected_categories=["Tone & Voice"]
        ),
        BenchmarkItem(
            id="TEST-05",
            title="Banned word 'hacks'",
            sample_text="Learn top 5 hacks to bypass standard KYC delays.",
            expected_issues_count=1,
            expected_categories=["Terminology"]
        ),
        BenchmarkItem(
            id="TEST-06",
            title="Banned word 'no questions asked'",
            sample_text="Get an instant return with no questions asked guaranteed.",
            expected_issues_count=2,
            expected_categories=["Terminology", "Claims & Facts"]
        ),
        BenchmarkItem(
            id="TEST-07",
            title="Compound slang and customer reference",
            sample_text="What's up customers, we are dropping brand new features today!",
            expected_issues_count=2,
            expected_categories=["Terminology", "Tone & Voice"]
        ),
        BenchmarkItem(
            id="TEST-08",
            title="Banned term 'risk-free'",
            sample_text="Invest in our yield aggregator for a completely risk-free 12% return.",
            expected_issues_count=1,
            expected_categories=["Claims & Facts"]
        ),
        BenchmarkItem(
            id="TEST-09",
            title="Banned term 'unlimited refund'",
            sample_text="We issue an unlimited refund for any transaction cancellation within 90 days.",
            expected_issues_count=1,
            expected_categories=["Terminology"]
        ),
        BenchmarkItem(
            id="TEST-10",
            title="Multiple banned vocabulary terms",
            sample_text="Our customers love our cheap services and quick hacks.",
            expected_issues_count=3,
            expected_categories=["Terminology"]
        ),

        # 11-20: Unsubstantiated & Superlative Claims
        BenchmarkItem(
            id="TEST-11",
            title="Superlative claim '#1 in India'",
            sample_text="ApexPay is ranked #1 in India for commercial wire transfers.",
            expected_issues_count=1,
            expected_categories=["Claims & Facts"]
        ),
        BenchmarkItem(
            id="TEST-12",
            title="Superlative claim 'best in india'",
            sample_text="Experience the best in India banking integration platform.",
            expected_issues_count=1,
            expected_categories=["Claims & Facts"]
        ),
        BenchmarkItem(
            id="TEST-13",
            title="Absolute availability '100% uptime guaranteed'",
            sample_text="ApexPay provides 100% uptime guaranteed across all global regions.",
            expected_issues_count=1,
            expected_categories=["Claims & Facts"]
        ),
        BenchmarkItem(
            id="TEST-14",
            title="Unverified clinical claim",
            sample_text="Our anti-stress workstation suite is clinically proven to boost developer focus by 80%.",
            expected_issues_count=1,
            expected_categories=["Claims & Facts"]
        ),
        BenchmarkItem(
            id="TEST-15",
            title="Expired promotional discount claim",
            sample_text="Sign up now for a flat 50% discount on Enterprise annual plan during Cyber Week.",
            expected_issues_count=1,
            expected_categories=["Claims & Facts"]
        ),
        BenchmarkItem(
            id="TEST-16",
            title="Absolute superlative 'zero risk'",
            sample_text="Our treasury engine guarantees zero risk on all currency hedges.",
            expected_issues_count=1,
            expected_categories=["Claims & Facts"]
        ),
        BenchmarkItem(
            id="TEST-17",
            title="Unverified numerical assertion '100x faster'",
            sample_text="ApexPay settlements are 100x faster than traditional SWIFT networks.",
            expected_issues_count=1,
            expected_categories=["Claims & Facts"]
        ),
        BenchmarkItem(
            id="TEST-18",
            title="Unverified market share superlative 'world's only'",
            sample_text="We are the world's only zero-latency banking orchestrator.",
            expected_issues_count=1,
            expected_categories=["Claims & Facts"]
        ),
        BenchmarkItem(
            id="TEST-19",
            title="Expired offer combined with banned term",
            sample_text="All customers get a flat 50% discount on Enterprise annual plan today only.",
            expected_issues_count=2,
            expected_categories=["Terminology", "Claims & Facts"]
        ),
        BenchmarkItem(
            id="TEST-20",
            title="Unsubstantiated guarantee phrase",
            sample_text="We give a guaranteed return on all corporate cash pools.",
            expected_issues_count=1,
            expected_categories=["Claims & Facts"]
        ),

        # 21-25: Tone, Voice & Pressure tactics
        BenchmarkItem(
            id="TEST-21",
            title="Aggressive sales FOMO tone",
            sample_text="Don't be stupid! Buy our plan right now before prices skyrocket tomorrow!",
            expected_issues_count=2,
            expected_categories=["Tone & Voice"]
        ),
        BenchmarkItem(
            id="TEST-22",
            title="Inappropriate emoji spam in formal context",
            sample_text="Our compliance audit failed today 🔥🔥 check out the chaos 😂",
            expected_issues_count=2,
            expected_categories=["Tone & Voice"]
        ),
        BenchmarkItem(
            id="TEST-23",
            title="Condescending customer service tone",
            sample_text="If you actually read the manual you wouldn't ask such obvious questions.",
            expected_issues_count=1,
            expected_categories=["Tone & Voice"]
        ),
        BenchmarkItem(
            id="TEST-24",
            title="Profanity / vulgarity test",
            sample_text="The competition's payment portal is absolute wtf garbage.",
            expected_issues_count=1,
            expected_categories=["Tone & Voice"]
        ),
        BenchmarkItem(
            id="TEST-25",
            title="Air Canada chatbot bereavement replica",
            sample_text="Sorry for your loss lol, we will issue an unlimited refund immediately.",
            expected_issues_count=2,
            expected_categories=["Tone & Voice", "Terminology"]
        ),

        # 26-30: Compliant or Benchmark Edge Cases
        BenchmarkItem(
            id="TEST-26",
            title="Approved Fact 01 verification",
            sample_text="ApexPay processes over 50 million transactions monthly with 99.99% high-availability SLA.",
            expected_issues_count=0,
            expected_categories=[]
        ),
        BenchmarkItem(
            id="TEST-27",
            title="Approved Fact 03 security certification",
            sample_text="ApexPay is a certified PCI-DSS Level 1 Service Provider and ISO/IEC 27001:2022 audited.",
            expected_issues_count=0,
            expected_categories=[]
        ),
        BenchmarkItem(
            id="TEST-28",
            title="Clean member-oriented newsletter copy",
            sample_text="We are thrilled to welcome our new enterprise members with 24/7 dedicated member concierge support.",
            expected_issues_count=0,
            expected_categories=[]
        ),
        BenchmarkItem(
            id="TEST-29",
            title="Compliant Starter Tier offer",
            sample_text="New partners receive zero transaction processing fees for the first 30 days on Starter tier.",
            expected_issues_count=0,
            expected_categories=[]
        ),
        BenchmarkItem(
            id="TEST-30",
            title="Complex multi-violation stress test",
            sample_text="Yo customers! ApexPay is the best in India with cheap rates, 100% uptime guaranteed, and unlimited refund hacks!",
            expected_issues_count=6,
            expected_categories=["Terminology", "Claims & Facts", "Tone & Voice"]
        )
    ]
    return test_cases

