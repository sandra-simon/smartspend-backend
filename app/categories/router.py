from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.categories.schema import (
    CategoryCreateRequest,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdateRequest,
)

from app.categories.service import (
    create_category,
    get_categories,
    update_category,
    delete_category,
)

from app.core.database import get_db
from app.core.dependencies import get_current_user_id


router = APIRouter(
    prefix="/api/v1/categories",
    tags=["Categories"],
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category_endpoint(
    data: CategoryCreateRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
) -> CategoryResponse:
    return create_category(
        db=db,
        user_id=user_id,
        data=data,
    )


@router.get(
    "",
    response_model=CategoryListResponse,
)
def list_categories(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    type: str | None = None,
    year: int | None = None,
    month: int | None = None,
) -> CategoryListResponse:
    if (year is None) != (month is None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_BUDGET_PERIOD",
                    "message": "Year and month must be provided together.",
                }
            },
        )
    if month is not None and not 1 <= month <= 12:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_BUDGET_PERIOD",
                    "message": "Month must be between 1 and 12.",
                }
            },
    )
    
    return get_categories(
        db=db,
        user_id=user_id,
        category_type=type,
        year=year,
        month=month,
    )


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category_endpoint(
    category_id: int,
    data: CategoryUpdateRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
) -> CategoryResponse:
    return update_category(
        db=db,
        user_id=user_id,
        category_id=category_id,
        data=data,
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category_endpoint(
    category_id: int,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
) -> None:
    delete_category(
        db=db,
        user_id=user_id,
        category_id=category_id,
    )