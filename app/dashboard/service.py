from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.dashboard import repository
from app.dashboard.schema import (
    DashboardCashflow,
    DashboardComparison,
    DashboardExpenseCategory,
    DashboardExpenseSplitResponse,
    DashboardPeriod,
    DashboardSummaryResponse,
    DashboardTopExpenseCategory,
)


def get_dashboard_summary(
    db: Session,
    user_id: int,
    year: int | None = None,
    month: int | None = None,
) -> DashboardSummaryResponse:
    if year is None or month is None:
        now = datetime.now(timezone.utc)
        year = now.year
        month = now.month

    # Current month totals
    total_income, total_expenses = repository.get_monthly_totals(
        db=db,
        user_id=user_id,
        year=year,
        month=month,
    )

    # Find previous month
    if month == 1:
        previous_year = year - 1
        previous_month = 12
    else:
        previous_year = year
        previous_month = month - 1

    # Previous month totals
    previous_income, previous_expenses = repository.get_monthly_totals(
        db=db,
        user_id=user_id,
        year=previous_year,
        month=previous_month,
    )

    net_available_capital = total_income - total_expenses
    previous_net_available_capital = (
        previous_income - previous_expenses
    )

    
        # Check whether the previous month has any transactions
    previous_month_has_data = repository.has_monthly_transactions(
        db=db,
        user_id=user_id,
        year=previous_year,
        month=previous_month,
    )

    # Calculate comparison only when previous-month data exists
    if not previous_month_has_data:
        net_available_capital_change_percentage = None
        net_available_capital_change = None
    elif (
        previous_net_available_capital <= 0
        or net_available_capital < 0
    ):
        net_available_capital_change_percentage = None
        net_available_capital_change = (
            net_available_capital - previous_net_available_capital
        )
    else:
        net_available_capital_change_percentage = (
            (
                net_available_capital
                - previous_net_available_capital
            )
            / previous_net_available_capital
        ) * Decimal("100")
        net_available_capital_change = None


    # Calculate burned and retained percentages

    if total_income > 0:
        burned_percentage = (
            total_expenses / total_income
        ) * Decimal("100")

        retained_percentage = (
            net_available_capital / total_income
        ) * Decimal("100")
    elif total_expenses > 0:
        burned_percentage = Decimal("100")
        retained_percentage = Decimal("0")
    else:
        burned_percentage = Decimal("0")
        retained_percentage = Decimal("0")


    previous_period_label = datetime(
        previous_year,
        previous_month,
        1,
    ).strftime("%B %Y")

    return DashboardSummaryResponse(
        period=DashboardPeriod(
            year=year,
            month=month,
        ),
        net_available_capital=net_available_capital,
        total_income=total_income,
        total_expenses=total_expenses,
        comparison=DashboardComparison(
            previous_period_label=previous_period_label,
            net_available_capital_change_percentage=(
                net_available_capital_change_percentage
            ),
            net_available_capital_change=net_available_capital_change,
        ),
        cashflow=DashboardCashflow(
            burned_percentage=burned_percentage,
            retained_percentage=retained_percentage,
        ),
    )


def get_dashboard_expense_split(
    db: Session,
    user_id: int,
    year: int | None = None,
    month: int | None = None,
) -> DashboardExpenseSplitResponse:
    if year is None or month is None:
        now = datetime.now(timezone.utc)
        year = now.year
        month = now.month

    rows = repository.get_monthly_expense_breakdown(
        db=db,
        user_id=user_id,
        year=year,
        month=month,
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
            DashboardExpenseCategory(
                category_id=row.category_id,
                category_name=row.name,
                amount=row.amount,
                percentage=percentage,
            )
        )

    top_category = None

    if categories:
        top_category = DashboardTopExpenseCategory(
            category_id=categories[0].category_id,
            category_name=categories[0].category_name,
            amount=categories[0].amount,
            percentage=categories[0].percentage,
        )

    return DashboardExpenseSplitResponse(
        period=DashboardPeriod(
            year=year,
            month=month,
        ),
        total_expenses=total_expenses,
        top_category=top_category,
        categories=categories,
    )