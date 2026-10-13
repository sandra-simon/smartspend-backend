from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class TransactionCreateRequest(BaseModel):
    category_id: int
    amount: Decimal = Field(gt=0)
    currency: str = "INR"
    title: str = Field(min_length=1, max_length=150)
    transaction_at: datetime
    merchant: str | None = Field(default=None, max_length=150)
    notes: str | None = None


class TransactionUpdateRequest(BaseModel):
    category_id: int | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    currency: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=150)
    transaction_at: datetime | None = None
    merchant: str | None = Field(default=None, max_length=150)
    notes: str | None = None


class TransactionCategoryResponse(BaseModel):
    category_id: int
    name: str
    type: str


class TransactionResponse(BaseModel):
    transaction_id: int
    type: str
    amount: Decimal
    currency: str
    category: TransactionCategoryResponse
    title: str
    merchant: str | None
    transaction_at: datetime


class MonthlyBudgetResponse(BaseModel):
    year: int
    month: int
    limit: Decimal
    spent: Decimal
    remaining: Decimal
    percentage_used: Decimal


class TransactionDetailResponse(TransactionResponse):
    notes: str | None
    created_at: datetime
    updated_at: datetime
    monthly_budget: MonthlyBudgetResponse | None


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    pagination: dict


class DailyNetTotalResponse(BaseModel):
    date: date
    income_total: Decimal
    expense_total: Decimal
    net_total: Decimal