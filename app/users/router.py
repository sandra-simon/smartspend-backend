from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.users.schema import UserResponse, UserUpdateRequest
from app.users.service import (
    get_current_user,
    update_current_user,
)


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
) -> UserResponse:
    return get_current_user(
        db=db,
        user_id=user_id,
    )


@router.patch(
    "/me",
    response_model=UserResponse,
)
def update_me(
    data: UserUpdateRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
) -> UserResponse:
    return update_current_user(
        db=db,
        user_id=user_id,
        data=data,
    )