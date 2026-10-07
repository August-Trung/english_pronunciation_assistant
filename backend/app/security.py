import os
import hmac
import hashlib
import json
import base64
import time
import sqlite3
from typing import Optional, List, Dict, Any
from fastapi import Header, HTTPException, Depends

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "fluent_academic_english_secret_key_2026_rbac_p0_secure")
PBKDF2_ITERATIONS = 100000

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def _base64url_decode(s: str) -> bytes:
    padding = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)

def hash_password(password: str) -> str:
    """Generate salted PBKDF2-HMAC-SHA256 password hash."""
    if not password:
        return ""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2:sha256:{PBKDF2_ITERATIONS}${salt.hex()}${key.hex()}"

def verify_password(plain_password: str, hashed: str) -> bool:
    """Verify password against salted PBKDF2 hash or legacy password hash."""
    if not plain_password or not hashed:
        return False
    try:
        if hashed.startswith("pbkdf2:sha256:"):
            parts = hashed.split('$')
            if len(parts) != 3:
                return False
            meta, salt_hex, key_hex = parts
            iterations = int(meta.split(':')[2])
            salt = bytes.fromhex(salt_hex)
            expected_key = bytes.fromhex(key_hex)
            computed_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, iterations)
            return hmac.compare_digest(computed_key, expected_key)
        else:
            # Fallback for upgrading plaintext / legacy passwords cleanly
            return hmac.compare_digest(plain_password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def create_access_token(user_id: int, email: str, role: str, tenant_id: Optional[str] = None, expires_hours: int = 72) -> str:
    """Create a tamper-proof signed JWT token using HMAC-SHA256."""
    header = {"alg": "HS256", "typ": "JWT"}
    exp_time = int(time.time()) + (expires_hours * 3600)
    payload = {
        "sub": str(user_id),
        "user_id": user_id,
        "email": email,
        "role": role,
        "tenant_id": str(tenant_id) if tenant_id is not None else None,
        "iat": int(time.time()),
        "exp": exp_time
    }
    
    header_b64 = _base64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(JWT_SECRET.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _base64url_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def decode_access_token(token: str) -> dict:
    """Validate token signature and expiration, returning token payload."""
    if not token:
        raise HTTPException(status_code=401, detail="Authentication token missing.")
    try:
        parts = token.strip().split('.')
        if len(parts) != 3:
            raise HTTPException(status_code=401, detail="Invalid token format.")
            
        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(JWT_SECRET.encode('utf-8'), signing_input, hashlib.sha256).digest()
        provided_sig = _base64url_decode(sig_b64)
        
        if not hmac.compare_digest(expected_sig, provided_sig):
            raise HTTPException(status_code=401, detail="Token signature invalid or tampered.")
            
        payload = json.loads(_base64url_decode(payload_b64).decode('utf-8'))
        
        if int(time.time()) > payload.get("exp", 0):
            raise HTTPException(status_code=401, detail="Authentication token expired. Please sign in again.")
            
        return payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")

def extract_bearer_token(authorization: Optional[str] = Header(None)) -> str:
    """Extract raw token string from Authorization Header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required. Bearer token missing.")
    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization scheme. Use 'Bearer <token>'.")
    return parts[1]

def get_current_user_from_db(db_path: str, token: str) -> dict:
    """Fetch active user record verified by cryptographic token."""
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    
    conn = sqlite3.connect(db_path, timeout=10.0)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, email, name, role, tenant_id, COALESCE(status, 'active')
            FROM users
            WHERE id = ? AND (IsXoa IS NULL OR IsXoa = 0)
        """, (user_id,))
    except Exception:
        cursor.execute("""
            SELECT id, email, name, role, tenant_id, 'active'
            FROM users
            WHERE id = ? AND (IsXoa IS NULL OR IsXoa = 0)
        """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=401, detail="Account not found or deactivated.")
        
    if row[5] == "suspended":
        raise HTTPException(status_code=403, detail="Account is suspended. Please contact your school administrator.")
        
    return {
        "id": row[0],
        "email": row[1],
        "name": row[2],
        "role": row[3],
        "tenant_id": str(row[4]) if row[4] is not None else None,
        "status": row[5]
    }

def record_audit_log(cursor, user_id: int, action: str, target_type: str, target_id: str, tenant_id: Optional[str], details: str = ""):
    """Insert immutable system audit entry."""
    try:
        cursor.execute("""
            INSERT INTO audit_logs (user_id, action, target_type, target_id, tenant_id, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, action, target_type, str(target_id), str(tenant_id) if tenant_id is not None else None, details))
    except Exception as e:
        print(f"Audit log write notice: {e}")
