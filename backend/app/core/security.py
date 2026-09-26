"""
MedExplain AI - Security Utilities

JWT authentication, password hashing, and current-doctor
authentication utilities.
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.doctor import Doctor


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password.
    """

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against its hashed version.
    """

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# ============================================================
# OAUTH2 / JWT CONFIGURATION
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token",
)


# ============================================================
# JWT TOKEN CREATION
# ============================================================

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.
    """

    to_encode = data.copy()

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expire = (
        datetime.now(timezone.utc)
        + expires_delta
    )

    to_encode.update(
        {
            "exp": expire,
        }
    )

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# ============================================================
# JWT TOKEN DECODING
# ============================================================

def decode_access_token(
    token: str,
) -> dict | None:
    """
    Decode and validate a JWT access token.

    Returns the decoded payload when valid.
    Returns None when the token is invalid or expired.
    """

    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

    except JWTError:
        return None


# ============================================================
# CURRENT AUTHENTICATED DOCTOR
# ============================================================

def get_current_doctor(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Doctor:
    """
    Get the currently authenticated doctor from the JWT token.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    # Decode JWT
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    # Extract doctor ID from token
    doctor_id = payload.get("sub")

    if doctor_id is None:
        raise credentials_exception

    # Convert doctor ID to integer
    try:
        doctor_id = int(doctor_id)

    except (TypeError, ValueError):
        raise credentials_exception

    # Find active doctor
    doctor = db.scalar(
        select(Doctor).where(
            Doctor.id == doctor_id,
            Doctor.is_active.is_(True),
        )
    )

    if doctor is None:
        raise credentials_exception

    return doctor