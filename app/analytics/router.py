from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.analytics.schema import (
    AnalyticsCashflowTrendResponse,
    AnalyticsSpendingBreakdownResponse,
    AnalyticsSummaryResponse,
    AnalyticsTopCategoriesResponse
)
from app.analytics.service import (
    get_analytics_summary,
    get_cashflow_trend,
    get_spending_breakdown,
    get_top_categories
)
from app.core.database import get_db
from app.core.dependencies import get_current_user_id


router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics"],
)


@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
)
def get_analytics_summary_endpoint(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    period: str = Query(default="monthly"),
) -> AnalyticsSummaryResponse:
    return get_analytics_summary(
        db=db,
        user_id=user_id,
        period=period,
    )


@router.get(
    "/spending-breakdown",
    response_model=AnalyticsSpendingBreakdownResponse,
)
def get_spending_breakdown_endpoint(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    period: str = Query(default="monthly"),
) -> AnalyticsSpendingBreakdownResponse:
    return get_spending_breakdown(
        db=db,
        user_id=user_id,
        period=period,
    )


@router.get(
    "/cashflow-trend",
    response_model=AnalyticsCashflowTrendResponse,
)
def get_cashflow_trend_endpoint(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    period: str = Query(default="monthly"),
) -> AnalyticsCashflowTrendResponse:
    return get_cashflow_trend(
        db=db,
        user_id=user_id,
        period=period,
    )


@router.get(
    "/top-categories",
    response_model=AnalyticsTopCategoriesResponse,
)
def get_top_categories_endpoint(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    period: str = Query(default="monthly"),
) -> AnalyticsTopCategoriesResponse:
    return get_top_categories(
        db=db,
        user_id=user_id,
        period=period,
    )