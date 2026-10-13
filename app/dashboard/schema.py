from pydantic import BaseModel
from decimal import Decimal

class DashboardPeriod(BaseModel):
    year: int
    month: int


class DashboardComparison(BaseModel):
    previous_period_label: str
    net_available_capital_change_percentage: float | None
    net_available_capital_change: Decimal | None


class DashboardCashflow(BaseModel):
    burned_percentage: float
    retained_percentage: float


class DashboardSummaryResponse(BaseModel):
    period: DashboardPeriod
    net_available_capital: float
    total_income: float
    total_expenses: float
    comparison: DashboardComparison
    cashflow: DashboardCashflow


class DashboardTopExpenseCategory(BaseModel):
    category_id: int
    category_name: str
    amount: float
    percentage: float


class DashboardExpenseCategory(BaseModel):
    category_id: int
    category_name: str
    amount: float
    percentage: float


class DashboardExpenseSplitResponse(BaseModel):
    period: DashboardPeriod
    total_expenses: float
    top_category: DashboardTopExpenseCategory | None
    categories: list[DashboardExpenseCategory]