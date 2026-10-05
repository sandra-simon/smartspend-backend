from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.categories import repository
from app.categories.model import Category
from app.transactions.model import Transaction
from app.categories.schema import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
    CategoryListResponse,
)
from app.budgets import repository as budget_repository


ALLOWED_CATEGORY_TYPES = {
    "income",
    "expense",
}


ALLOWED_ICONS = {
    "food",
    "shopping",
    "transport",
    "home",
    "health",
    "education",
    "bills",
    "entertainment",
    "travel",
    "salary",
    "gift",
    "investment",
    "fitness",
    "pets",
}


def create_category(
    db: Session,
    user_id: int,
    data: CategoryCreateRequest,
) -> CategoryResponse:
    if data.type not in ALLOWED_CATEGORY_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_CATEGORY_TYPE",
                    "message": "Category type must be income or expense.",
                }
            },
        )

    if data.icon not in ALLOWED_ICONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_CATEGORY_ICON",
                    "message": "Invalid category icon.",
                }
            },
        )

    existing_category = repository.get_category_by_name(
        db=db,
        user_id=user_id,
        name=data.name,
    )

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "CATEGORY_ALREADY_EXISTS",
                    "message": "A category with this name already exists.",
                }
            },
        )

    category = repository.create_category(
        db=db,
        user_id=user_id,
        name=data.name,
        icon=data.icon,
        type=data.type,
    )

    return CategoryResponse(
        category_id=category.category_id,
        name=category.name,
        icon=category.icon,
        type=category.type,
        monthly_limit=None,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def update_category(
    db: Session,
    user_id: int,
    category_id: int,
    data: CategoryUpdateRequest,
) -> CategoryResponse:
    category = repository.get_category_by_id(
        db=db,
        user_id=user_id,
        category_id=category_id,
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "CATEGORY_NOT_FOUND",
                    "message": "Category not found.",
                }
            },
        )

    if data.type is not None and data.type not in ALLOWED_CATEGORY_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_CATEGORY_TYPE",
                    "message": "Category type must be income or expense.",
                }
            },
        )

    if data.type is not None and data.type != category.type:
        transaction_exists = (
            db.query(Transaction)
            .filter(
                Transaction.category_id == category_id,
                Transaction.user_id == user_id,
            )
            .first()
            is not None
        )

        if transaction_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "CATEGORY_TYPE_IN_USE",
                        "message": "Category type cannot be changed because the category is used by transactions.",
                    }
                },
            )

    if data.icon is not None and data.icon not in ALLOWED_ICONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_CATEGORY_ICON",
                    "message": "Invalid category icon.",
                }
            },
        )

    if data.name is not None:
        existing_category = repository.get_category_by_name(
            db=db,
            user_id=user_id,
            name=data.name,
        )

        if (
            existing_category
            and existing_category.category_id != category_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "CATEGORY_ALREADY_EXISTS",
                        "message": "A category with this name already exists.",
                    }
                },
            )

    category = repository.update_category(
        db=db,
        category=category,
        name=data.name,
        icon=data.icon,
        type=data.type,
    )

    current_date = datetime.now(timezone.utc)

    budget = repository.get_applicable_budget(
        db=db,
        category_id=category.category_id,
        year=current_date.year,
        month=current_date.month,
    )

    monthly_limit = budget.limit_amount if budget else None

    return CategoryResponse(
        category_id=category.category_id,
        name=category.name,
        icon=category.icon,
        type=category.type,
        monthly_limit=monthly_limit,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def delete_category(
    db: Session,
    user_id: int,
    category_id: int,
) -> None:
    category = repository.get_category_by_id(
        db=db,
        user_id=user_id,
        category_id=category_id,
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "CATEGORY_NOT_FOUND",
                    "message": "Category not found.",
                }
            },
        )

    transaction_exists = (
        db.query(Transaction)
        .filter(
            Transaction.category_id == category_id,
            Transaction.user_id == user_id,
        )
        .first()
        is not None
    )

    if transaction_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "CATEGORY_IN_USE",
                    "message": "Category cannot be deleted because it is used by transactions.",
                }
            },
        )
    
    budget_repository.delete_budgets_for_category(
        db=db,
        category_id=category_id,
    )

    repository.delete_category(
        db=db,
        category=category,
    )


def get_categories(
    db: Session,
    user_id: int,
    category_type: str | None = None,
    year: int | None = None,
    month: int | None = None,
) -> CategoryListResponse:
    if category_type is not None and category_type not in ALLOWED_CATEGORY_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_CATEGORY_TYPE",
                    "message": "Category type must be income or expense.",
                }
            },
        )

    categories = repository.get_categories(
        db=db,
        user_id=user_id,
        category_type=category_type,
    )

    categories_response = []

    for category in categories:

        if year is None and month is None:
            current_date = datetime.now(timezone.utc)
            budget_year = current_date.year
            budget_month = current_date.month
        else:
            budget_year = year
            budget_month = month

        monthly_limit = None

        budget = repository.get_applicable_budget(
            db=db,
            category_id=category.category_id,
            year=budget_year,
            month=budget_month,
        )

        if budget:
            monthly_limit = budget.limit_amount

        categories_response.append(
            CategoryResponse(
                category_id=category.category_id,
                name=category.name,
                icon=category.icon,
                type=category.type,
                monthly_limit=monthly_limit,
                created_at=category.created_at,
                updated_at=category.updated_at,
            )
        )

    return CategoryListResponse(
        categories=categories_response
    )