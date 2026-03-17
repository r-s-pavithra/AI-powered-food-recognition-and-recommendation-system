import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
import hashlib
from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def _normalized_password_bytes(password: str) -> bytes:
    """
    Pre-hash passwords before bcrypt to avoid bcrypt 72-byte truncation collisions.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")

def hash_password(password: str) -> str:
    """Hash password using bcrypt with SHA-256 pre-hashing."""
    password_bytes = _normalized_password_bytes(password)
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password.
    Supports both:
    - new SHA-256+bcrypt hashes
    - legacy direct bcrypt flow (with 72-byte truncation) for backward compatibility
    """
    # Encode the stored hash
    hashed_bytes = hashed_password.encode('utf-8')
    # Verify new format first
    if bcrypt.checkpw(_normalized_password_bytes(plain_password), hashed_bytes):
        return True
    # Fallback for legacy hashes
    legacy_password_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(legacy_password_bytes, hashed_bytes)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
