from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    icon: str = Field(min_length=1, max_length=100)
    type: str


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    icon: str | None = Field(default=None, min_length=1, max_length=100)
    type: str | None = None


class CategoryResponse(BaseModel):
    category_id: int
    name: str
    icon: str
    type: str
    monthly_limit: Decimal | None
    created_at: datetime
    updated_at: datetime


class CategoryListResponse(BaseModel):
    categories: list[CategoryResponse]