import os
import re
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pathlib import Path
from dotenv import load_dotenv

from .database import SessionLocal
from . import models

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# =========================
# PASSWORD HASHING
# =========================
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# =========================
# JWT CONFIG
# =========================
def get_secret_key():
    """Get SECRET_KEY from environment variables. Fails gracefully if missing."""
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        # Try reading from .env file directly
        if env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and line.startswith("SECRET_KEY="):
                            key_value = line.split("=", 1)[1]
                            key_value = key_value.strip().strip('"').strip("'")
                            if key_value:
                                secret_key = key_value
                                break
            except Exception as e:
                pass  # Will raise error below
    
    if not secret_key:
        raise ValueError(
            "SECRET_KEY environment variable is required. "
            "Please set SECRET_KEY in backend/.env file. "
            "Generate a secure key with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )
    
    if len(secret_key) < 32:
        raise ValueError(
            "SECRET_KEY must be at least 32 characters long for security. "
            "Generate a secure key with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )
    
    return secret_key.strip()

SECRET_KEY = get_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# =========================
# DB DEPENDENCY
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# PASSWORD FUNCTIONS
# =========================
def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    return True, ""

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# =========================
# TOKEN FUNCTIONS
# =========================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# =========================
# CURRENT USER (🔥 FIX)
# =========================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception

    return user
