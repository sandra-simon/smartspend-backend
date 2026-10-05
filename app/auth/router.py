from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.auth.schema import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    PasswordUpdateRequest,
)
from app.auth.service import (
    register_user,
    login_user,
    refresh_access_token,
    forgot_password,
    update_password,
)
from app.core.database import get_db
from app.core.dependencies import (
    get_current_user_id,
    get_optional_user_id,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
) -> RegisterResponse:
    return register_user(
        db=db,
        data=data,
    )

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    return login_user(
        db=db,
        data=data,
    )

@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
)
def refresh_token(
    data: RefreshTokenRequest,
) -> RefreshTokenResponse:
    return refresh_access_token(data)


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
)
def forgot_password_endpoint(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> ForgotPasswordResponse:
    message = forgot_password(
        db=db,
        email=data.email,
    )

    return ForgotPasswordResponse(
        message=message,
    )


@router.post(
    "/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def update_password_endpoint(
    data: PasswordUpdateRequest,
    db: Session = Depends(get_db),
    user_id: Annotated[
        int | None,
        Depends(get_optional_user_id),
    ] = None,
) -> None:
    update_password(
        db=db,
        data=data,
        user_id=user_id,
    )