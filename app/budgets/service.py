from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo

from app.budgets import repository
from app.budgets.schema import BudgetRequest, BudgetResponse
from app.categories.model import Category

IST = ZoneInfo("Asia/Kolkata")

def get_budget(
    db: Session,
    user_id: int,
    category_id: int,
    year: int | None = None,
    month: int | None = None,
) -> BudgetResponse:
    category = db.get(Category, category_id)

    if not category or category.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "CATEGORY_NOT_FOUND",
                    "message": "Category not found.",
                }
            },
        )

    if year is None and month is None:
        now = datetime.now(IST)
        year = now.year
        month = now.month

    budget = repository.get_applicable_budget(
        db=db,
        category_id=category_id,
        year=year,
        month=month,
    )

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "BUDGET_NOT_FOUND",
                    "message": "No budget has been established for this category.",
                }
            },
        )

    return BudgetResponse(
        budget_id=budget.budget_id,
        category_id=category_id,
        year=year,
        month=month,
        limit_amount=budget.limit_amount,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


def set_budget(
    db: Session,
    user_id: int,
    category_id: int,
    data: BudgetRequest,
) -> BudgetResponse:
    category = db.get(Category, category_id)

    if not category or category.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "CATEGORY_NOT_FOUND",
                    "message": "Category not found.",
                }
            },
        )

    if category.type != "expense":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "BUDGET_NOT_ALLOWED",
                    "message": "Budgets can only be set for expense categories.",
                }
            },
        )

    now = datetime.now(IST)
    year = now.year
    month = now.month

    budget = repository.get_budget(
        db=db,
        category_id=category_id,
        year=year,
        month=month,
    )

    if budget:
        budget = repository.update_budget(
            db=db,
            budget=budget,
            limit_amount=data.limit_amount,
        )
    else:
        budget = repository.create_budget(
            db=db,
            category_id=category_id,
            year=year,
            month=month,
            limit_amount=data.limit_amount,
        )

    return BudgetResponse(
        budget_id=budget.budget_id,
        category_id=category_id,
        year=year,
        month=month,
        limit_amount=budget.limit_amount,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


def clear_budget(
    db: Session,
    user_id: int,
    category_id: int,
) -> BudgetResponse:
    category = db.get(Category, category_id)

    if not category or category.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "CATEGORY_NOT_FOUND",
                    "message": "Category not found.",
                }
            },
        )

    if category.type != "expense":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "BUDGET_NOT_ALLOWED",
                    "message": "Budgets can only be cleared for expense categories.",
                }
            },
        )

    now = datetime.now(IST)
    year = now.year
    month = now.month

    budget = repository.get_budget(
        db=db,
        category_id=category_id,
        year=year,
        month=month,
    )

    if budget:
        budget = repository.update_budget(
            db=db,
            budget=budget,
            limit_amount=None,
        )
    else:
        budget = repository.create_budget(
            db=db,
            category_id=category_id,
            year=year,
            month=month,
            limit_amount=None,
        )

    return BudgetResponse(
        budget_id=budget.budget_id,
        category_id=category_id,
        year=year,
        month=month,
        limit_amount=None,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


def delete_budget(
    db: Session,
    user_id: int,
    category_id: int,
) -> None:
    category = db.get(Category, category_id)

    if not category or category.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "CATEGORY_NOT_FOUND",
                    "message": "Category not found.",
                }
            },
        )

    if category.type != "expense":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "BUDGET_NOT_ALLOWED",
                    "message": "Budgets can only be cleared for expense categories.",
                }
            },
        )

    now = datetime.now(IST)
    year = now.year
    month = now.month

    budget = repository.get_budget(
        db=db,
        category_id=category_id,
        year=year,
        month=month,
    )

    if budget:
        repository.update_budget(
            db=db,
            budget=budget,
            limit_amount=None,
        )
    else:
        repository.create_budget(
            db=db,
            category_id=category_id,
            year=year,
            month=month,
            limit_amount=None,
        )