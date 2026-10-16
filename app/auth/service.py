from datetime import datetime, timedelta, timezone
from app.categories.defaults import create_default_categories

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.email import send_password_reset_email
from app.auth import repository
from app.auth.schema import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    PasswordUpdateRequest,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
    create_password_reset_token,
    hash_password_reset_token
)

def register_user(
    db: Session,
    data: RegisterRequest,
) -> RegisterResponse:
    existing_user = repository.get_user_by_email(
        db,
        data.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "EMAIL_ALREADY_EXISTS",
                    "message": "An account with this email already exists.",
                }
            },
        )

    password_hash = hash_password(data.password)

    try:
        user = repository.create_user(
            db=db,
            username=data.username,
            email=data.email,
            password_hash=password_hash,
        )

        create_default_categories(
            db=db,
            user_id=user.user_id,
        )

        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise

    return RegisterResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
    )


def login_user(
    db: Session,
    data: LoginRequest,
) -> LoginResponse:
    user = repository.get_user_by_email(
        db,
        data.email,
    )

    if not user or not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password.",
                }
            },
        )

    access_token = create_access_token(
        user_id=user.user_id,
        expires_delta=timedelta(minutes=30),
    )
    refresh_token = create_refresh_token(
        user_id=user.user_id,
        expires_delta=timedelta(days=30),
    )

    return LoginResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        access_token=access_token,
        refresh_token=refresh_token,
    )


def refresh_access_token(
    data: RefreshTokenRequest,
) -> RefreshTokenResponse:
    user_id = decode_refresh_token(
        data.refresh_token
    )

    access_token = create_access_token(
        user_id=user_id,
        expires_delta=timedelta(minutes=30),
    )

    return RefreshTokenResponse(
        access_token=access_token,
    )


def forgot_password(
    db: Session,
    email: str,
) -> str:
    user = repository.get_user_by_email(
        db,
        email,
    )

    message = (
        "If an account exists with this email, "
        "a password reset link has been sent."
    )

    if not user:
        return message

    reset_token = create_password_reset_token()
    reset_token_hash = hash_password_reset_token(
        reset_token
    )

    user.reset_token_hash = reset_token_hash
    user.reset_token_expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    db.commit()

    send_password_reset_email(
        recipient_email=user.email,
        reset_token=reset_token,
    )

    return message


def update_password(
    db: Session,
    data: PasswordUpdateRequest,
    user_id: int | None = None,
) -> None:
    # Forgot-password reset flow
    if data.reset_token:
        reset_token_hash = hash_password_reset_token(
            data.reset_token
        )

        user = repository.get_user_by_reset_token_hash(
            db,
            reset_token_hash,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_OR_EXPIRED_RESET_TOKEN",
                        "message": "Invalid or expired password reset token.",
                    }
                },
            )

        if (
            not user.reset_token_expires_at
            or user.reset_token_expires_at
            < datetime.now(timezone.utc)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_OR_EXPIRED_RESET_TOKEN",
                        "message": "Invalid or expired password reset token.",
                    }
                },
            )

    # Authenticated password-change flow
    else:
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "AUTHENTICATION_REQUIRED",
                        "message": "Authentication is required.",
                    }
                },
            )

        user = repository.get_user_by_id(
            db,
            user_id,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "message": "User not found.",
                    }
                },
            )

        if not data.current_password or not verify_password(
            data.current_password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_CURRENT_PASSWORD",
                        "message": "Current password is incorrect.",
                    }
                },
            )

    user.password_hash = hash_password(data.new_password)

    # Reset tokens are single-use.
    user.reset_token_hash = None
    user.reset_token_expires_at = None

    db.commit()