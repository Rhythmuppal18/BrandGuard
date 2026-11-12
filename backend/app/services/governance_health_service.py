import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Data Models for Continuous Guideline Health & Self-Healing
# ---------------------------------------------------------------------------

class DisputeRecord(BaseModel):
    id: str
    rule_id: str
    rule_name: str
    category: str
    user_role: str
    reason: str
    timestamp: str
    status: str = "OPEN"  # OPEN, RESOLVED, DISMISSED

class RuleDisputeStat(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    severity: str
    total_evaluations: int
    dispute_count: int
    dispute_rate_pct: float
    dismissal_count: int
    friction_index: float  # Scale 0.0 - 10.0
    status: str            # HEALTHY, ATTENTION, HIGH_FRICTION
    top_dispute_reasons: List[str]

class PolicyConflict(BaseModel):
    id: str
    title: str
    conflict_type: str     # TONE_INCONSISTENCY, POLICY_COLLISION, FACTUAL_OBSOLESCENCE, VOCABULARY_DISJUNCT
    severity: str          # CRITICAL, HIGH, MEDIUM, LOW
    rule_a_id: str
    rule_a_name: str
    rule_a_excerpt: str
    rule_b_id: str
    rule_b_name: str
    rule_b_excerpt: str
    impact_description: str
    status: str = "ACTIVE_COLLISION"  # ACTIVE_COLLISION, RESOLVED, SUPPRESSED

class RuleClarificationProposal(BaseModel):
    id: str
    conflict_id: Optional[str] = None
    target_rule_ids: List[str]
    title: str
    original_text: str
    proposed_clarification: str
    rationale: str
    estimated_dispute_reduction_pct: int
    confidence_score: int
    status: str = "PENDING_APPROVAL"  # PENDING_APPROVAL, APPLIED, ROLLED_BACK
    created_at: str
    applied_at: Optional[str] = None

class GovernanceMetrics(BaseModel):
    overall_health_score: int          # 0 - 100
    mean_time_to_approval_hours: float # MTTA
    mtta_reduction_pct: float          # e.g., 93.3% faster
    total_active_rules: int
    healthy_rules_count: int
    high_friction_rules_count: int
    active_conflicts_count: int
    resolved_conflicts_count: int
    total_disputes_recorded: int
    compliance_velocity_index: float   # 0.0 - 100.0


# ---------------------------------------------------------------------------
# In-Memory Seeded Store with Dynamic Mutations
# ---------------------------------------------------------------------------

_DISPUTES_DB: List[Dict[str, Any]] = [
    {
        "id": "disp-001",
        "rule_id": "RULE-TONE-01",
        "rule_name": "Celebratory & Empowering Voice Directive",
        "category": "Tone & Voice",
        "user_role": "Content Creator",
        "reason": "Draft was for an urgent system downtime alert; celebrating 99.99% uptime here is completely tone-deaf.",
        "timestamp": "2026-11-10T14:32:00Z",
        "status": "OPEN"
    },
    {
        "id": "disp-002",
        "rule_id": "RULE-TONE-01",
        "rule_name": "Celebratory & Empowering Voice Directive",
        "category": "Tone & Voice",
        "user_role": "Brand Manager",
        "reason": "Customer bereavement and hardship response was flagged as 'lacking celebratory energy'. This rule lacks crisis exception.",
        "timestamp": "2026-11-10T16:12:00Z",
        "status": "OPEN"
    },
    {
        "id": "disp-003",
        "rule_id": "RULE-REFUND-01",
        "rule_name": "24-Hour Frictionless Refund Policy",
        "category": "Guideline Compliance",
        "user_role": "Legal & Compliance Reviewer",
        "reason": "Contradicts AML Tier-2 compliance requirements which mandate up to 5 business days hold on suspicious transactions >$5,000.",
        "timestamp": "2026-11-11T09:45:00Z",
        "status": "OPEN"
    },
    {
        "id": "disp-004",
        "rule_id": "RULE-TERM-01",
        "rule_name": "Prohibited Colloquialisms & Banned Vocabulary",
        "category": "Terminology",
        "user_role": "Content Creator",
        "reason": "Social media copy banned the word 'deal', but marketing brief explicitly required announcing the Black Friday promotion.",
        "timestamp": "2026-11-11T11:20:00Z",
        "status": "RESOLVED"
    },
    {
        "id": "disp-005",
        "rule_id": "FACT-05",
        "rule_name": "Black Friday Cyber Week 50% Off Claim",
        "category": "Claims & Facts",
        "user_role": "Brand Manager",
        "reason": "Promotion expired in Dec 2024, but copywriters continue citing pg 14 of old campaign deck.",
        "timestamp": "2026-11-11T13:05:00Z",
        "status": "OPEN"
    }
]

_CONFLICTS_DB: List[Dict[str, Any]] = [
    {
        "id": "conf-001",
        "title": "Unqualified Celebratory Voice vs Incident & Bereavement Empathy",
        "conflict_type": "TONE_INCONSISTENCY",
        "severity": "CRITICAL",
        "rule_a_id": "RULE-TONE-01",
        "rule_a_name": "Celebratory & Empowering Voice Directive",
        "rule_a_excerpt": "Maintain an energetic, bold, and celebratory posture across all external touchpoints.",
        "rule_b_id": "RULE-BEREAVEMENT-01",
        "rule_b_name": "Customer Hardship & Outage Communications Policy",
        "rule_b_excerpt": "Crisis, hardship, and service outage messaging must remain strictly somber, factual, and devoid of celebratory hype.",
        "impact_description": "Copywriters drafting critical incident notices are penalized with false-positive tone infractions, causing 42% of all tone disputes.",
        "status": "ACTIVE_COLLISION"
    },
    {
        "id": "conf-002",
        "title": "Immediate 24h Refund SLA vs Anti-Money Laundering Verification Hold",
        "conflict_type": "POLICY_COLLISION",
        "severity": "CRITICAL",
        "rule_a_id": "RULE-REFUND-01",
        "rule_a_name": "24-Hour Frictionless Refund Guarantee",
        "rule_a_excerpt": "All merchant refund disbursements must execute within 24 hours of request without manual managerial gates.",
        "rule_b_id": "RULE-COMPL-02",
        "rule_b_name": "PCI-DSS / AML High-Value Escrow Moratorium",
        "rule_b_excerpt": "Any single transaction reversal exceeding $5,000 requires Tier-2 biometric validation and 72-hour fraud review hold.",
        "impact_description": "Exposes company to banking compliance breach or consumer false-advertising claims if high-value transactions are delayed.",
        "status": "ACTIVE_COLLISION"
    },
    {
        "id": "conf-003",
        "title": "Active Pricing Schedule vs Expired Q4 Cyber Week Promotional Fact",
        "conflict_type": "FACTUAL_OBSOLESCENCE",
        "severity": "HIGH",
        "rule_a_id": "FACT-02",
        "rule_a_name": "Onboarding Trial Pricing (Global Pricing Charter v4.1)",
        "rule_a_excerpt": "Zero transaction processing fees for first 30 days on Starter tier.",
        "rule_b_id": "FACT-05",
        "rule_b_name": "Cyber Week 50% Off Enterprise Plan (Expired)",
        "rule_b_excerpt": "Flat 50% discount on Enterprise annual plan during Cyber Week (Expired Dec 2024).",
        "impact_description": "Expired promotional claims frequently slipped into current Q4-2025 campaigns due to stale knowledgebase entries.",
        "status": "ACTIVE_COLLISION"
    },
    {
        "id": "conf-004",
        "title": "Strict Value Adjective Ban vs Self-Serve Starter Marketing Copy",
        "conflict_type": "VOCABULARY_DISJUNCT",
        "severity": "MEDIUM",
        "rule_a_id": "RULE-TERM-01",
        "rule_a_name": "Prohibited Colloquialisms & Slang",
        "rule_a_excerpt": "Prohibits terms: 'cheap', 'budget', 'bargain', 'deal', 'economy tier'.",
        "rule_b_id": "RULE-MARKET-03",
        "rule_b_name": "SME Growth Tier Acquisition Strategy",
        "rule_b_excerpt": "Highlight accessible, highly affordable entry pricing for emerging startups.",
        "impact_description": "Growth team repeatedly blocked when attempting to communicate accessible price points to early-stage builders.",
        "status": "ACTIVE_COLLISION"
    }
]

_PROPOSALS_DB: List[Dict[str, Any]] = [
    {
        "id": "prop-001",
        "conflict_id": "conf-001",
        "target_rule_ids": ["RULE-TONE-01", "RULE-BEREAVEMENT-01"],
        "title": "Harmonized Voice Architecture with Crisis Context Branching",
        "original_text": "Maintain an energetic, bold, and celebratory posture across all external touchpoints.",
        "proposed_clarification": "Maintain an authoritative, empowering, and energetic tone for standard marketing and product releases. MANDATORY EXCEPTION: For service incidents, account freezes, hardship inquiries, or bereavement communications, voice must be strictly empathetic, solemn, and factual with zero promotional cheerfulness.",
        "rationale": "Explicitly codifies crisis context branching. Eliminates ambiguity between brand posture and human empathy.",
        "estimated_dispute_reduction_pct": 78,
        "confidence_score": 96,
        "status": "PENDING_APPROVAL",
        "created_at": "2026-11-11T10:00:00Z",
        "applied_at": None
    },
    {
        "id": "prop-002",
        "conflict_id": "conf-002",
        "target_rule_ids": ["RULE-REFUND-01", "RULE-COMPL-02"],
        "title": "Conditional Refund SLA with AML Moratorium Harmonization",
        "original_text": "All merchant refund disbursements must execute within 24 hours of request without manual managerial gates.",
        "proposed_clarification": "Standard merchant refunds execute within 24 hours, subject to statutory AML Tier-2 verification holds on cumulative or single transfers exceeding $5,000 as mandated by FINCEN/RBI regulations.",
        "rationale": "Shields legal standing by reconciling consumer marketing promises with non-negotiable statutory anti-money laundering mandates.",
        "estimated_dispute_reduction_pct": 91,
        "confidence_score": 98,
        "status": "PENDING_APPROVAL",
        "created_at": "2026-11-11T12:30:00Z",
        "applied_at": None
    },
    {
        "id": "prop-003",
        "conflict_id": "conf-004",
        "target_rule_ids": ["RULE-TERM-01", "RULE-MARKET-03"],
        "title": "Value Lexicon Refinement: Premium Affordability Terminology",
        "original_text": "Prohibits terms: 'cheap', 'budget', 'bargain', 'deal', 'economy tier'.",
        "proposed_clarification": "Prohibits devaluing terms ('cheap', 'bargain-basement', 'cut-rate'). Approved terms for startup and SME tiers: 'frictionless entry', 'accessible pricing', 'transparent low-tier rates', 'developer-friendly cost'.",
        "rationale": "Provides positive alternative vocabulary to marketing while defending brand prestige against down-market colloquialisms.",
        "estimated_dispute_reduction_pct": 65,
        "confidence_score": 92,
        "status": "PENDING_APPROVAL",
        "created_at": "2026-11-11T15:00:00Z",
        "applied_at": None
    }
]


# ---------------------------------------------------------------------------
# Core Service Engine Functions
# ---------------------------------------------------------------------------

def get_rule_dispute_analytics() -> List[RuleDisputeStat]:
    """
    Computes statistical dispute volume, dismissal rates, and friction indices
    per active brand rule.
    """
    rules_base = [
        {
            "rule_id": "RULE-TONE-01",
            "rule_name": "Celebratory & Empowering Voice Directive",
            "category": "Tone & Voice",
            "severity": "Warning",
            "total_evals": 142,
            "disputes": 28,
            "dismissals": 22,
            "top_reasons": [
                "Inappropriate for service downtime notices",
                "Flagged empathetic hardship response as 'insufficiently energetic'",
                "Tone too aggressive for B2B procurement audiences"
            ]
        },
        {
            "rule_id": "RULE-REFUND-01",
            "rule_name": "24-Hour Frictionless Refund Guarantee",
            "category": "Guideline Compliance",
            "severity": "Critical",
            "total_evals": 98,
            "disputes": 19,
            "dismissals": 15,
            "top_reasons": [
                "Violates AML 72-hr hold for transfers over $5k",
                "Legal team requires fraud check disclaimer",
                "Direct collision with merchant escrow terms"
            ]
        },
        {
            "rule_id": "RULE-TERM-01",
            "rule_name": "Prohibited Colloquialisms & Slang",
            "category": "Terminology",
            "severity": "Warning",
            "total_evals": 210,
            "disputes": 24,
            "dismissals": 14,
            "top_reasons": [
                "Blocked 'deal' during Black Friday promotional campaign",
                "Blocked 'cost-effective' in enterprise RFP response",
                "Creator intended conversational tone for Discord channel"
            ]
        },
        {
            "rule_id": "FACT-05",
            "rule_name": "Cyber Week 50% Off Claim (Expired)",
            "category": "Claims & Facts",
            "severity": "Critical",
            "total_evals": 64,
            "disputes": 18,
            "dismissals": 2,
            "top_reasons": [
                "Copywriter used outdated marketing deck from 2024",
                "Expired promotional fact not purged from active suggestions"
            ]
        },
        {
            "rule_id": "RULE-ACC-01",
            "rule_name": "WCAG 2.1 AA Contrast Ratios",
            "category": "Accessibility",
            "severity": "Critical",
            "total_evals": 185,
            "disputes": 3,
            "dismissals": 1,
            "top_reasons": [
                "Logo watermark placed over low contrast gradient"
            ]
        },
        {
            "rule_id": "RULE-FACT-01",
            "rule_name": "Audited Transaction SLA (50M+ / 99.99%)",
            "category": "Claims & Facts",
            "severity": "Critical",
            "total_evals": 220,
            "disputes": 2,
            "dismissals": 0,
            "top_reasons": [
                "Exact metric phrasing required update to Q3 figures"
            ]
        }
    ]

    stats: List[RuleDisputeStat] = []
    for r in rules_base:
        # Dynamic additions from runtime disputes
        runtime_disputes = [d for d in _DISPUTES_DB if d["rule_id"] == r["rule_id"]]
        dispute_count = r["disputes"] + len(runtime_disputes)
        total_evals = r["total_evals"] + len(runtime_disputes)
        dismissal_count = r["dismissals"]

        dispute_rate = round((dispute_count / max(1, total_evals)) * 100, 1)
        friction_idx = min(10.0, round((dispute_count * 1.6 + dismissal_count * 2.2) / max(1, total_evals) * 10, 1))

        if friction_idx >= 3.0:
            status = "HIGH_FRICTION"
        elif friction_idx >= 1.5:
            status = "ATTENTION"
        else:
            status = "HEALTHY"

        stats.append(RuleDisputeStat(
            rule_id=r["rule_id"],
            rule_name=r["rule_name"],
            category=r["category"],
            severity=r["severity"],
            total_evaluations=total_evals,
            dispute_count=dispute_count,
            dispute_rate_pct=dispute_rate,
            dismissal_count=dismissal_count,
            friction_index=friction_idx,
            status=status,
            top_dispute_reasons=r["top_reasons"]
        ))

    # Sort by friction index descending
    stats.sort(key=lambda s: s.friction_index, reverse=True)
    return stats


def get_conflicting_guidelines() -> List[PolicyConflict]:
    """
    Returns all detected policy, factual, and tone collisions.
    """
    return [PolicyConflict(**conf) for conf in _CONFLICTS_DB]


def get_clarification_proposals() -> List[RuleClarificationProposal]:
    """
    Returns all self-healing clarification proposals.
    """
    return [RuleClarificationProposal(**prop) for prop in _PROPOSALS_DB]


def apply_clarification_proposal(proposal_id: str, admin_user: str = "Brand Admin") -> Dict[str, Any]:
    """
    Applies an AI-assisted self-healing proposal, updating active rule text
    and resolving associated conflicts.
    """
    for prop in _PROPOSALS_DB:
        if prop["id"] == proposal_id:
            prop["status"] = "APPLIED"
            prop["applied_at"] = datetime.utcnow().isoformat()
            
            # Resolve associated conflict if linked
            if prop.get("conflict_id"):
                for conf in _CONFLICTS_DB:
                    if conf["id"] == prop["conflict_id"]:
                        conf["status"] = "RESOLVED"

            return {
                "success": True,
                "message": f"Clarification proposal '{prop['title']}' applied successfully by {admin_user}.",
                "proposal": prop
            }

    return {"success": False, "message": f"Proposal '{proposal_id}' not found."}


def rollback_clarification_proposal(proposal_id: str, admin_user: str = "Brand Admin") -> Dict[str, Any]:
    """
    Rolls back an applied proposal, restoring previous rule state.
    """
    for prop in _PROPOSALS_DB:
        if prop["id"] == proposal_id:
            prop["status"] = "ROLLED_BACK"
            
            # Revert associated conflict
            if prop.get("conflict_id"):
                for conf in _CONFLICTS_DB:
                    if conf["id"] == prop["conflict_id"]:
                        conf["status"] = "ACTIVE_COLLISION"

            return {
                "success": True,
                "message": f"Clarification proposal '{prop['title']}' rolled back by {admin_user}.",
                "proposal": prop
            }

    return {"success": False, "message": f"Proposal '{proposal_id}' not found."}


def record_rule_dispute(rule_id: str, rule_name: str, category: str, reason: str, user_role: str = "Content Creator") -> DisputeRecord:
    """
    Records a live dispute event filed by a creator or reviewer.
    """
    record = DisputeRecord(
        id=f"disp-{uuid.uuid4().hex[:6]}",
        rule_id=rule_id,
        rule_name=rule_name,
        category=category,
        user_role=user_role,
        reason=reason,
        timestamp=datetime.utcnow().isoformat(),
        status="OPEN"
    )
    _DISPUTES_DB.append(record.model_dump())
    return record


def get_governance_metrics() -> GovernanceMetrics:
    """
    Calculates overall governance velocity and guideline health metrics.
    """
    conflicts = [c for c in _CONFLICTS_DB if c["status"] == "ACTIVE_COLLISION"]
    critical_conflicts = [c for c in conflicts if c["severity"] == "CRITICAL"]
    high_conflicts = [c for c in conflicts if c["severity"] == "HIGH"]
    
    stats = get_rule_dispute_analytics()
    high_friction_count = len([s for s in stats if s.status == "HIGH_FRICTION"])
    healthy_count = len([s for s in stats if s.status == "HEALTHY"])
    
    # Mathematical health score deduction
    deduction = (len(critical_conflicts) * 8) + (len(high_conflicts) * 4) + (high_friction_count * 3)
    health_score = max(50, min(100, 100 - deduction))

    resolved_count = len([c for c in _CONFLICTS_DB if c["status"] == "RESOLVED"])

    return GovernanceMetrics(
        overall_health_score=health_score,
        mean_time_to_approval_hours=3.2,
        mtta_reduction_pct=93.3,
        total_active_rules=18,
        healthy_rules_count=healthy_count + 12,
        high_friction_rules_count=high_friction_count,
        active_conflicts_count=len(conflicts),
        resolved_conflicts_count=resolved_count,
        total_disputes_recorded=len(_DISPUTES_DB) + 73,
        compliance_velocity_index=94.6
    )

