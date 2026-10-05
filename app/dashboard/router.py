from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.dashboard.schema import (
    DashboardExpenseSplitResponse,
    DashboardSummaryResponse,
)
from app.dashboard.service import (
    get_dashboard_expense_split,
    get_dashboard_summary,
)


router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
)
def get_dashboard_summary_endpoint(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    year: int | None = Query(default=None),
    month: int | None = Query(default=None, ge=1, le=12),
) -> DashboardSummaryResponse:
    return get_dashboard_summary(
        db=db,
        user_id=user_id,
        year=year,
        month=month,
    )


@router.get(
    "/expense-split",
    response_model=DashboardExpenseSplitResponse,
)
def get_dashboard_expense_split_endpoint(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    year: int | None = Query(default=None),
    month: int | None = Query(default=None, ge=1, le=12),
) -> DashboardExpenseSplitResponse:
    return get_dashboard_expense_split(
        db=db,
        user_id=user_id,
        year=year,
        month=month,
    )