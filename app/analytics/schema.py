from pydantic import BaseModel


class AnalyticsPeriod(BaseModel):
    period: str
    label: str


class AnalyticsComparison(BaseModel):
    previous_period_label: str
    income_change_percentage: float | None
    expense_change_percentage: float | None
    net_savings_change_percentage: float | None


class AnalyticsSummaryResponse(BaseModel):
    period: AnalyticsPeriod
    total_income: float
    total_expenses: float
    net_savings: float
    comparison: AnalyticsComparison


class AnalyticsSpendingCategory(BaseModel):
    category_id: int
    category_name: str
    amount: float
    percentage: float


class AnalyticsSpendingBreakdownResponse(BaseModel):
    period: AnalyticsPeriod
    total_expenses: float
    top_category: AnalyticsSpendingCategory | None
    categories: list[AnalyticsSpendingCategory]


class AnalyticsCashflowPoint(BaseModel):
    label: str
    income: float
    expenses: float


class AnalyticsCashflowTrendResponse(BaseModel):
    period: AnalyticsPeriod
    granularity: str
    data: list[AnalyticsCashflowPoint]


class AnalyticsTopCategory(BaseModel):
    category_id: int
    category_name: str
    icon: str
    transaction_count: int
    spent: float
    budget: float | None
    remaining: float | None
    percentage_used: float | None


class AnalyticsTopCategoriesResponse(BaseModel):
    period: AnalyticsPeriod
    categories: list[AnalyticsTopCategory]