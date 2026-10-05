from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.users import repository
from app.users.schema import UserResponse, UserUpdateRequest

def get_current_user(
    db: Session,
    user_id: int,
) -> UserResponse:
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

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        joined_at=user.joined_at,
        theme=user.theme,
    )

def update_current_user(
    db: Session,
    user_id: int,
    data: UserUpdateRequest,
) -> UserResponse:
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

    if data.username is None and data.theme is None:
        return UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            joined_at=user.joined_at,
            theme=user.theme,
        )

    user = repository.update_user(
        db=db,
        user=user,
        username=data.username,
        theme=data.theme,
    )

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        joined_at=user.joined_at,
        theme=user.theme,
    )