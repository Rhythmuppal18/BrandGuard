from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class RoleEnum(str, Enum):
    CREATOR = "Creator"
    MANAGER = "Brand Manager"
    REVIEWER = "Legal & Compliance Reviewer"
    ADMIN = "Brand Admin"

class StatusEnum(str, Enum):
    DRAFT = "Draft"
    AUTO_CHECKED = "Auto-Checked"
    IN_REVIEW = "In Review"
    CHANGES_REQUESTED = "Changes Requested"
    APPROVED = "Approved"

class SeverityEnum(str, Enum):
    CRITICAL = "Critical"
    WARNING = "Warning"
    SUGGESTION = "Suggestion"

class CategoryEnum(str, Enum):
    TERMINOLOGY = "Terminology"
    CLAIMS_FACTS = "Claims & Facts"
    TONE_VOICE = "Tone & Voice"
    GUIDELINE = "Guideline Compliance"
    ACCESSIBILITY = "Accessibility"

class SuggestionStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EDITED = "edited"

class ApprovedFact(BaseModel):
    id: str
    claim_key: str
    statement: str
    source_document: str
    verified_by: str
    valid_from: str
    expires_at: Optional[str] = None
    is_active: bool = True

class BrandRule(BaseModel):
    id: str
    category: CategoryEnum
    title: str
    description: str
    citation: str
    severity: SeverityEnum

class BannedTerm(BaseModel):
    id: str
    term: str
    reason: str
    suggested_replacement: str
    rule_id: str

class PreferredTerm(BaseModel):
    id: str
    preferred: str
    context: str
    rule_id: str

class BrandKit(BaseModel):
    brand_name: str = "ApexPay Global"
    mission: str = "Secure, transparent enterprise financial infrastructure"
    tone_primary: str = "Professional, precise, customer-first"
    prohibited_tones: List[str] = ["Casual slang", "Overly aggressive sales", "Hyperbolic guarantees", "Condescending"]
    approved_facts: List[ApprovedFact] = []
    banned_terms: List[BannedTerm] = []
    preferred_terms: List[PreferredTerm] = []
    brand_rules: List[BrandRule] = []

class Finding(BaseModel):
    id: str
    category: CategoryEnum
    severity: SeverityEnum
    matched_text: str
    start_char: int = -1
    end_char: int = -1
    explanation: str
    rule_id: str
    rule_name: str
    citation_source: str
    confidence_score: int
    fact_status: Optional[str] = None  # "SUPPORTED", "UNSUPPORTED", "EXPIRED", "CONTRADICTS"
    suggested_fix: str

class TrackedChange(BaseModel):
    id: str
    finding_id: str
    original_text: str
    replacement_text: str
    start_char: int
    end_char: int
    status: SuggestionStatus = SuggestionStatus.PENDING
    rejection_reason: Optional[str] = None
    edited_text: Optional[str] = None

class Comment(BaseModel):
    id: str
    author: str
    role: str
    comment_text: str
    created_at: str

class AuditLogEntry(BaseModel):
    id: str
    timestamp: str
    actor: str
    role: str
    action: str
    details: str
    content_hash: str

class ContentVersion(BaseModel):
    version_number: int
    content: str
    created_at: str
    created_by: str
    change_summary: str
    score: int

class ReviewRequest(BaseModel):
    title: Optional[str] = "Untitled Content"
    content: str
    content_type: str = "social_post" # social_post, press_release, support_notice, marketing_email, blog
    brand_name: Optional[str] = "ApexPay Global"
    target_tone: Optional[str] = "professional and friendly"

class ReviewAnalysisResponse(BaseModel):
    content_id: Optional[str] = None
    title: str
    content_type: str
    original_content: str
    current_content: str
    brand_score: int
    category_scores: Dict[str, int]
    findings: List[Finding]
    tracked_changes: List[TrackedChange]
    status: StatusEnum
    created_at: str
    updated_at: str
    audit_trail: List[AuditLogEntry]
    note: str

class SuggestionActionRequest(BaseModel):
    action: str  # "accept", "reject", "edit"
    actor: str = "Creator"
    role: str = "Creator"
    rejection_reason: Optional[str] = None
    edited_text: Optional[str] = None

class TransitionRequest(BaseModel):
    target_status: StatusEnum
    actor: str
    role: str
    comment: Optional[str] = None

class CommentCreateRequest(BaseModel):
    author: str
    role: str
    comment_text: str

class BenchmarkItem(BaseModel):
    id: str
    title: str
    sample_text: str
    expected_issues_count: int
    expected_categories: List[str]
    actual_detected_count: int = 0
    actual_score: int = 100
    matched_correctly: bool = False
    latency_ms: float = 0.0

class FileUploadRequest(BaseModel):
    filename: str
    file_base64: str
    content_type: Optional[str] = "social_post"
    title: Optional[str] = None

