"""
MedExplain AI - Authentication Schemas

Pydantic schemas for registration and login.
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """
    Data required for doctor login.
    """

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    JWT token returned after successful authentication.
    """

    access_token: str
    token_type: str = "bearer"