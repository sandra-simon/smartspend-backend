from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetRequest(BaseModel):
    limit_amount: Decimal = Field(gt=0)


class BudgetResponse(BaseModel):
    budget_id: int
    category_id: int
    year: int
    month: int
    limit_amount: Decimal
    created_at: datetime
    updated_at: datetime