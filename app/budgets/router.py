from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.budgets.schema import BudgetRequest, BudgetResponse
from app.budgets.service import (
    delete_budget,
    get_budget,
    set_budget,
)
from app.core.database import get_db
from app.core.dependencies import get_current_user_id


router = APIRouter(
    prefix="/api/v1/categories/{category_id}/budget",
    tags=["Budgets"],
)


@router.get(
    "",
    response_model=BudgetResponse,
)
def get_budget_endpoint(
    category_id: int,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    year: int | None = Query(default=None, ge=2000),
    month: int | None = Query(default=None, ge=1, le=12),
) -> BudgetResponse:

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

    return get_budget(
        db=db,
        user_id=user_id,
        category_id=category_id,
        year=year,
        month=month,
    )


@router.put(
    "",
    response_model=BudgetResponse,
)
def set_budget_endpoint(
    category_id: int,
    data: BudgetRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
) -> BudgetResponse:
    return set_budget(
        db=db,
        user_id=user_id,
        category_id=category_id,
        data=data,
    )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_budget_endpoint(
    category_id: int,
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
) -> None:
    delete_budget(
        db=db,
        user_id=user_id,
        category_id=category_id,
    )