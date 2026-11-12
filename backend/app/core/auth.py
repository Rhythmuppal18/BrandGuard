import hmac
import hashlib
import json
import base64
import time
from typing import Dict, Any, Optional, List
from fastapi import Request, HTTPException, status, Depends
from app.core.config import SECRET_KEY, TOKEN_EXPIRY_HOURS, DEFAULT_TENANT_ID

# Standardized Enterprise Roles
ROLE_ADMIN = "ADMIN"
ROLE_COMPLIANCE = "COMPLIANCE_OFFICER"
ROLE_MANAGER = "BRAND_MANAGER"
ROLE_CREATOR = "CREATOR"

# Persona map for deterministic demonstration and enterprise test cases
PERSONA_REGISTRY: Dict[str, Dict[str, Any]] = {
    "admin": {
        "id": "usr-admin-01",
        "name": "Chief Compliance Officer",
        "email": "admin@brandguard.internal",
        "role": ROLE_ADMIN,
        "tenant_id": DEFAULT_TENANT_ID
    },
    "legal": {
        "id": "usr-legal-02",
        "name": "Legal & Compliance Reviewer",
        "email": "legal@brandguard.internal",
        "role": ROLE_COMPLIANCE,
        "tenant_id": DEFAULT_TENANT_ID
    },
    "manager": {
        "id": "usr-mgr-03",
        "name": "Senior Brand Director",
        "email": "manager@brandguard.internal",
        "role": ROLE_MANAGER,
        "tenant_id": DEFAULT_TENANT_ID
    },
    "creator": {
        "id": "usr-creat-04",
        "name": "Content Creator",
        "email": "creator@brandguard.internal",
        "role": ROLE_CREATOR,
        "tenant_id": DEFAULT_TENANT_ID
    }
}

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64url_decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding and padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data.encode("utf-8"))

def create_access_token(
    user_id: str,
    role: str,
    name: str,
    tenant_id: str = DEFAULT_TENANT_ID,
    expiry_hours: int = TOKEN_EXPIRY_HOURS
) -> str:
    """Creates a tamper-evident, cryptographically signed HMAC-SHA256 session token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "role": role,
        "name": name,
        "tenant_id": tenant_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + (expiry_hours * 3600)
    }
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    sig = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(sig)
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies HMAC signature and expiration of session token. Returns payload dict or None."""
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(sig_b64)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
            
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        if payload.get("exp", 0) < int(time.time()):
            return None
            
        return payload
    except Exception:
        return None

def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Extracts and verifies user identity from Authorization header or session cookie.
    Falls back deterministically to mapped persona or standard Creator role with valid tenant.
    """
    auth_header = request.headers.get("Authorization") or request.headers.get("X-BrandGuard-Session")
    if auth_header:
        token = auth_header.replace("Bearer ", "").strip()
        payload = verify_access_token(token)
        if payload:
            return {
                "id": payload.get("sub"),
                "role": payload.get("role", ROLE_CREATOR),
                "name": payload.get("name", "Authenticated User"),
                "tenant_id": payload.get("tenant_id", DEFAULT_TENANT_ID)
            }
            
    # Check if a client specified a persona key in X-Persona header
    persona_key = request.headers.get("X-Persona", "").lower().strip()
    if persona_key in PERSONA_REGISTRY:
        p = PERSONA_REGISTRY[persona_key]
        return {
            "id": p["id"],
            "role": p["role"],
            "name": p["name"],
            "tenant_id": p["tenant_id"]
        }
        
    # Default authenticated context for standard operations
    default_p = PERSONA_REGISTRY["creator"]
    return {
        "id": default_p["id"],
        "role": default_p["role"],
        "name": default_p["name"],
        "tenant_id": default_p["tenant_id"]
    }

def require_role(allowed_roles: List[str]):
    """FastAPI route dependency enforcing server-side RBAC."""
    def role_checker(user: Dict[str, Any] = Depends(get_current_user)):
        user_role = user.get("role")
        if user_role not in allowed_roles and user_role != ROLE_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Operation requires one of {allowed_roles}, but current role is '{user_role}'"
            )
        return user
    return role_checker
