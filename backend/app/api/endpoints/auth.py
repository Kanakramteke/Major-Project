"""
MedExplain AI - Authentication Endpoints

Doctor registration and login APIs.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.database.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.doctor import DoctorCreate, DoctorResponse
from app.services.auth_service import (
    authenticate_doctor,
    create_doctor,
    get_doctor_by_email,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new doctor account.
    """

    existing_doctor = get_doctor_by_email(
        db,
        doctor_data.email,
    )

    if existing_doctor is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A doctor with this email already exists.",
        )

    doctor = create_doctor(
        db,
        doctor_data,
    )

    return doctor


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate a doctor using JSON credentials.

    This endpoint is used by the React frontend.
    """

    doctor = authenticate_doctor(
        db,
        login_data.email,
        login_data.password,
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        {
            "sub": str(doctor.id),
            "email": doctor.email,
        }
    )

    return TokenResponse(
        access_token=access_token,
    )


@router.post(
    "/token",
    response_model=TokenResponse,
)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible login endpoint used by Swagger UI.

    Swagger sends the doctor's email in the username field.
    """

    doctor = authenticate_doctor(
        db,
        form_data.username,
        form_data.password,
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    access_token = create_access_token(
        {
            "sub": str(doctor.id),
            "email": doctor.email,
        }
    )

    return TokenResponse(
        access_token=access_token,
    )