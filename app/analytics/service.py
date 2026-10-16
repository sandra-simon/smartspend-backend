from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from decimal import Decimal

from sqlalchemy.orm import Session

from app.budgets import repository as budget_repository
from app.analytics import repository
from app.analytics.schema import (
    AnalyticsCashflowPoint,
    AnalyticsCashflowTrendResponse,
    AnalyticsComparison,
    AnalyticsPeriod,
    AnalyticsSpendingBreakdownResponse,
    AnalyticsSpendingCategory,
    AnalyticsSummaryResponse,
    AnalyticsTopCategoriesResponse,
    AnalyticsTopCategory,
)

IST = ZoneInfo("Asia/Kolkata")
VALID_PERIODS = {"weekly", "monthly", "yearly"}


def validate_period(period: str) -> str:
    if period not in VALID_PERIODS:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_ANALYTICS_PERIOD",
                    "message": "Period must be weekly, monthly, or yearly.",
                }
            },
        )

    return period



def get_period_ranges(
    period: str,
) -> tuple[datetime, datetime, datetime, datetime]:
    now = datetime.now(IST)

    if period == "weekly":
        current_start = (
            now - timedelta(days=now.weekday())
        ).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        current_end = current_start + timedelta(days=7)
        previous_start = current_start - timedelta(days=7)
        previous_end = current_start

    elif period == "monthly":
        current_start = now.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        if current_start.month == 12:
            current_end = current_start.replace(
                year=current_start.year + 1,
                month=1,
            )
        else:
            current_end = current_start.replace(
                month=current_start.month + 1,
            )

        if current_start.month == 1:
            previous_start = current_start.replace(
                year=current_start.year - 1,
                month=12,
            )
        else:
            previous_start = current_start.replace(
                month=current_start.month - 1,
            )

        previous_end = current_start

    else:
        current_start = now.replace(
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        current_end = current_start.replace(
            year=current_start.year + 1,
        )
        previous_start = current_start.replace(
            year=current_start.year - 1,
        )
        previous_end = current_start

    return (
        current_start,
        current_end,
        previous_start,
        previous_end,
    )


def get_period_label(
    period: str,
    start_date: datetime,
    end_date: datetime,
) -> str:
    if period == "weekly":
        return (
            f"{start_date.strftime('%d')}–"
            f"{(end_date - timedelta(days=1)).strftime('%d %b %Y')}"
        )

    if period == "monthly":
        return start_date.strftime("%B %Y")

    return start_date.strftime("%Y")


def calculate_change_percentage(
    current: Decimal,
    previous: Decimal,
) -> Decimal | None:
    if previous == 0:
        return None

    return (
        (current - previous)
        / abs(previous)
    ) * Decimal("100")


def get_analytics_summary(
    db: Session,
    user_id: int,
    period: str = "monthly",
) -> AnalyticsSummaryResponse:
    period = validate_period(period)

    (
        current_start,
        current_end,
        previous_start,
        previous_end,
    ) = get_period_ranges(period)

    current_income, current_expenses = (
        repository.get_totals_for_range(
            db=db,
            user_id=user_id,
            start_date=current_start,
            end_date=current_end,
        )
    )

    previous_income, previous_expenses = (
        repository.get_totals_for_range(
            db=db,
            user_id=user_id,
            start_date=previous_start,
            end_date=previous_end,
        )
    )

    current_net_savings = current_income - current_expenses
    previous_net_savings = previous_income - previous_expenses

    income_change = calculate_change_percentage(
        current_income,
        previous_income,
    )

    expense_change = calculate_change_percentage(
        current_expenses,
        previous_expenses,
    )

    net_savings_change = calculate_change_percentage(
        current_net_savings,
        previous_net_savings,
    )

    current_label = get_period_label(
        period,
        current_start,
        current_end,
    )

    previous_label = get_period_label(
        period,
        previous_start,
        previous_end,
    )

    return AnalyticsSummaryResponse(
        period=AnalyticsPeriod(
            period=period,
            label=current_label,
        ),
        total_income=current_income,
        total_expenses=current_expenses,
        net_savings=current_net_savings,
        comparison=AnalyticsComparison(
            previous_period_label=previous_label,
            income_change_percentage=income_change,
            expense_change_percentage=expense_change,
            net_savings_change_percentage=net_savings_change,
        ),
    )


def get_spending_breakdown(
    db: Session,
    user_id: int,
    period: str = "monthly",
) -> AnalyticsSpendingBreakdownResponse:
    period = validate_period(period)

    (
        current_start,
        current_end,
        _,
        _,
    ) = get_period_ranges(period)

    rows = repository.get_expense_breakdown_for_range(
        db=db,
        user_id=user_id,
        start_date=current_start,
        end_date=current_end,
    )

    total_expenses = sum(
        (row.amount for row in rows),
        Decimal("0"),
    )

    categories = []

    for row in rows:
        percentage = (
            (row.amount / total_expenses) * Decimal("100")
            if total_expenses > 0
            else Decimal("0")
        )

        categories.append(
            AnalyticsSpendingCategory(
                category_id=row.category_id,
                category_name=row.name,
                amount=row.amount,
                percentage=percentage,
            )
        )

    top_category = categories[0] if categories else None

    period_label = get_period_label(
        period,
        current_start,
        current_end,
    )

    return AnalyticsSpendingBreakdownResponse(
        period=AnalyticsPeriod(
            period=period,
            label=period_label,
        ),
        total_expenses=total_expenses,
        top_category=top_category,
        categories=categories,
    )


def get_cashflow_trend(
    db: Session,
    user_id: int,
    period: str = "monthly",
) -> AnalyticsCashflowTrendResponse:
    period = validate_period(period)

    (
        current_start,
        current_end,
        _,
        _,
    ) = get_period_ranges(period)

    if period == "weekly":
        granularity = "day"
    elif period == "monthly":
        granularity = "week"
    else:
        granularity = "month"

    rows = repository.get_cashflow_for_range(
        db=db,
        user_id=user_id,
        start_date=current_start,
        end_date=current_end,
        granularity=granularity,
    )

    # Store database results by their period and transaction type.
    grouped_data = {}

    for row in rows:
        period_start = row.period_start
        transaction_type = row.type
        amount = row.amount

        if period_start not in grouped_data:
            grouped_data[period_start] = {
                "income": Decimal("0"),
                "expenses": Decimal("0"),
            }

        if transaction_type == "income":
            grouped_data[period_start]["income"] = amount
        elif transaction_type == "expense":
            grouped_data[period_start]["expenses"] = amount

    data = []

    if period == "weekly":
        # 7 daily points
        for day_offset in range(7):
            point_date = current_start + timedelta(days=day_offset)

            income = Decimal("0")
            expenses = Decimal("0")

            for period_start, values in grouped_data.items():
                if period_start.date() == point_date.date():
                    income = values["income"]
                    expenses = values["expenses"]
                    break

            data.append(
                AnalyticsCashflowPoint(
                    label=point_date.strftime("%a"),
                    income=income,
                    expenses=expenses,
                )
            )

    elif period == "monthly":
        # Calendar weeks represented within the selected month.
        first_week_start = (
            current_start
            - timedelta(days=current_start.weekday())
        )

        week_start = first_week_start
        week_number = 1

        while week_start < current_end:
            income = Decimal("0")
            expenses = Decimal("0")

            for period_start, values in grouped_data.items():
                if period_start.date() == week_start.date():
                    income = values["income"]
                    expenses = values["expenses"]
                    break

            data.append(
                AnalyticsCashflowPoint(
                    label=f"Week {week_number}",
                    income=income,
                    expenses=expenses,
                )
            )

            week_start += timedelta(days=7)
            week_number += 1

    else:
        # 12 monthly points
        for month_offset in range(12):
            month_start = current_start.replace(
                month=month_offset + 1,
            )

            income = Decimal("0")
            expenses = Decimal("0")

            for period_start, values in grouped_data.items():
                if (
                    period_start.year == month_start.year
                    and period_start.month == month_start.month
                ):
                    income = values["income"]
                    expenses = values["expenses"]
                    break

            data.append(
                AnalyticsCashflowPoint(
                    label=month_start.strftime("%b"),
                    income=income,
                    expenses=expenses,
                )
            )

    period_label = get_period_label(
        period,
        current_start,
        current_end,
    )

    return AnalyticsCashflowTrendResponse(
        period=AnalyticsPeriod(
            period=period,
            label=period_label,
        ),
        granularity=granularity,
        data=data,
    )


def get_top_categories(
    db: Session,
    user_id: int,
    period: str = "monthly",
) -> AnalyticsTopCategoriesResponse:
    period = validate_period(period)

    (
        current_start,
        current_end,
        _,
        _,
    ) = get_period_ranges(period)

    rows = repository.get_top_categories_for_range(
        db=db,
        user_id=user_id,
        start_date=current_start,
        end_date=current_end,
    )

    categories = []

    for row in rows:
        spent = Decimal(str(row.spent))

        if period == "yearly":
            monthly_budgets = []

            for month in range(1, 13):
                monthly_budget = budget_repository.get_applicable_budget(
                    db=db,
                    category_id=row.category_id,
                    year=current_start.year,
                    month=month,
                )

                if (
                    monthly_budget is None
                    or monthly_budget.limit_amount is None
                ):
                    monthly_budgets = []
                    break

                monthly_budgets.append(
                    Decimal(str(monthly_budget.limit_amount))
                )

            if len(monthly_budgets) == 12:
                limit = sum(monthly_budgets, Decimal("0"))
                remaining = limit - spent

                percentage_used = (
                    (spent / limit) * Decimal("100")
                    if limit > 0
                    else None
                )

                budget_value = float(limit)
                remaining_value = float(remaining)
                percentage_value = (
                    float(percentage_used)
                    if percentage_used is not None
                    else None
                )
            else:
                budget_value = None
                remaining_value = None
                percentage_value = None

        else:
            budget = budget_repository.get_applicable_budget(
                db=db,
                category_id=row.category_id,
                year=current_start.year,
                month=current_start.month,
            )

            if budget is not None and budget.limit_amount is not None:
                limit = Decimal(str(budget.limit_amount))
                remaining = limit - spent

                percentage_used = (
                    (spent / limit) * Decimal("100")
                    if limit > 0
                    else None
                )

                budget_value = float(limit)
                remaining_value = float(remaining)
                percentage_value = (
                    float(percentage_used)
                    if percentage_used is not None
                    else None
                )
            else:
                budget_value = None
                remaining_value = None
                percentage_value = None

        categories.append(
            AnalyticsTopCategory(
                category_id=row.category_id,
                category_name=row.name,
                icon=row.icon,
                transaction_count=row.transaction_count,
                spent=float(spent),
                budget=budget_value,
                remaining=remaining_value,
                percentage_used=percentage_value,
            )
        )

    period_label = get_period_label(
        period,
        current_start,
        current_end,
    )

    return AnalyticsTopCategoriesResponse(
        period=AnalyticsPeriod(
            period=period,
            label=period_label,
        ),
        categories=categories,
    )