from decimal import Decimal
from math import ceil

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.budgets import repository as budget_repository
from app.categories.model import Category
from app.transactions import repository
from app.transactions.schema import (
    DailyNetTotalResponse,
    MonthlyBudgetResponse,
    TransactionCreateRequest,
    TransactionDetailResponse,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdateRequest,
)


def create_transaction(
    db: Session,
    user_id: int,
    data: TransactionCreateRequest,
) -> TransactionResponse:
    category = db.get(
        Category,
        data.category_id,
    )

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

    if data.currency != "INR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_CURRENCY",
                    "message": "Currency must be INR.",
                }
            },
        )

    transaction = repository.create_transaction(
        db=db,
        user_id=user_id,
        category_id=data.category_id,
        amount=data.amount,
        currency=data.currency,
        title=data.title,
        transaction_at=data.transaction_at,
        merchant=data.merchant,
        notes=data.notes,
    )

    return TransactionResponse(
        transaction_id=transaction.transaction_id,
        type=category.type,
        amount=transaction.amount,
        currency=transaction.currency,
        category={
            "category_id": category.category_id,
            "name": category.name,
            "type": category.type,
        },
        title=transaction.title,
        merchant=transaction.merchant,
        transaction_at=transaction.transaction_at,
    )


def get_transactions(
    db: Session,
    user_id: int,
    type: str | None = None,
    page: int = 1,
    page_size: int = 20,
    category_id: int | None = None,
    search: str | None = None,
    date_from=None,
    date_to=None,
    sort_by: str = "transaction_at",
    sort_order: str = "desc",
) -> TransactionListResponse:

    offset = (page - 1) * page_size

    transactions, total = repository.get_transactions(
        db=db,
        user_id=user_id,
        type=type,
        category_id=category_id,
        search=search,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        offset=offset,
        limit=page_size,
    )

    items = []

    for transaction in transactions:
        category = transaction.category

        if not category:
            continue

        items.append(
            TransactionResponse(
                transaction_id=transaction.transaction_id,
                type=category.type,
                amount=transaction.amount,
                currency=transaction.currency,
                category={
                    "category_id": category.category_id,
                    "name": category.name,
                    "type": category.type,
                },
                title=transaction.title,
                merchant=transaction.merchant,
                transaction_at=transaction.transaction_at,
            )
        )

    total_pages = ceil(total / page_size) if total else 0

    return TransactionListResponse(
        items=items,
        pagination={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        },
    )


def get_daily_net_totals(
    db: Session,
    user_id: int,
    type: str | None = None,
    category_id: int | None = None,
    search: str | None = None,
    date_from=None,
    date_to=None,
) -> list[DailyNetTotalResponse]:
    totals = repository.get_daily_net_totals(
        db=db,
        user_id=user_id,
        type=type,
        category_id=category_id,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )

    return [
        DailyNetTotalResponse(**daily_total)
        for daily_total in totals
    ]


def get_transaction_detail(
    db: Session,
    user_id: int,
    transaction_id: int,
) -> TransactionDetailResponse:
    transaction = repository.get_transaction_by_id(
        db=db,
        user_id=user_id,
        transaction_id=transaction_id,
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "TRANSACTION_NOT_FOUND",
                    "message": "Transaction not found.",
                }
            },
        )

    category = transaction.category

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

    monthly_budget = None

    if category.type == "expense":
        transaction_year = transaction.transaction_at.year
        transaction_month = transaction.transaction_at.month

        budget = budget_repository.get_applicable_budget(
            db=db,
            category_id=category.category_id,
            year=transaction_year,
            month=transaction_month,
        )

        if budget:
            spent = budget_repository.get_category_monthly_spent(
                db=db,
                category_id=category.category_id,
                year=transaction_year,
                month=transaction_month,
            )

            remaining = budget.limit_amount - spent

            percentage_used = (
                (spent / budget.limit_amount) * Decimal("100")
                if budget.limit_amount > 0
                else Decimal("0")
            )

            monthly_budget = MonthlyBudgetResponse(
                year=transaction_year,
                month=transaction_month,
                limit=budget.limit_amount,
                spent=spent,
                remaining=remaining,
                percentage_used=percentage_used,
            )

    return TransactionDetailResponse(
        transaction_id=transaction.transaction_id,
        type=category.type,
        amount=transaction.amount,
        currency=transaction.currency,
        category={
            "category_id": category.category_id,
            "name": category.name,
            "type": category.type,
        },
        title=transaction.title,
        merchant=transaction.merchant,
        transaction_at=transaction.transaction_at,
        notes=transaction.notes,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at,
        monthly_budget=monthly_budget,
    )


def update_transaction(
    db: Session,
    user_id: int,
    transaction_id: int,
    data: TransactionUpdateRequest,
) -> TransactionResponse:
    transaction = repository.get_transaction_by_id(
        db=db,
        user_id=user_id,
        transaction_id=transaction_id,
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "TRANSACTION_NOT_FOUND",
                    "message": "Transaction not found.",
                }
            },
        )

    if data.category_id is not None:
        category = db.get(Category, data.category_id)

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
    else:
        category = db.get(Category, transaction.category_id)

    if data.currency is not None and data.currency != "INR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_CURRENCY",
                    "message": "Currency must be INR.",
                }
            },
        )

    update_data = {
        "category_id": data.category_id,
        "amount": data.amount,
        "currency": data.currency,
        "title": data.title,
        "transaction_at": data.transaction_at,
    }

    if "merchant" in data.model_fields_set:
        update_data["merchant"] = data.merchant

    if "notes" in data.model_fields_set:
        update_data["notes"] = data.notes

    transaction = repository.update_transaction(
        db=db,
        transaction=transaction,
        **update_data,
    )

    return TransactionResponse(
        transaction_id=transaction.transaction_id,
        type=category.type,
        amount=transaction.amount,
        currency=transaction.currency,
        category={
            "category_id": category.category_id,
            "name": category.name,
            "type": category.type,
        },
        title=transaction.title,
        merchant=transaction.merchant,
        transaction_at=transaction.transaction_at,
    )


def delete_transaction(
    db: Session,
    user_id: int,
    transaction_id: int,
) -> None:
    transaction = repository.get_transaction_by_id(
        db=db,
        user_id=user_id,
        transaction_id=transaction_id,
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "TRANSACTION_NOT_FOUND",
                    "message": "Transaction not found.",
                }
            },
        )

    repository.delete_transaction(
        db=db,
        transaction=transaction,
    )