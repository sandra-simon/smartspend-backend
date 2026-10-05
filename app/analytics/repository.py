from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.categories.model import Category
from app.transactions.model import Transaction


def get_totals_for_range(
    db: Session,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
) -> tuple:
    statement = (
        select(
            Category.type,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .join(
            Category,
            Category.category_id == Transaction.category_id,
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_at >= start_date,
            Transaction.transaction_at < end_date,
        )
        .group_by(Category.type)
    )

    results = db.execute(statement).all()

    total_income = 0
    total_expenses = 0

    for transaction_type, amount in results:
        if transaction_type == "income":
            total_income = amount
        elif transaction_type == "expense":
            total_expenses = amount

    return total_income, total_expenses


def get_expense_breakdown_for_range(
    db: Session,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
) -> list:
    statement = (
        select(
            Category.category_id,
            Category.name,
            func.sum(Transaction.amount).label("amount"),
        )
        .join(
            Transaction,
            Transaction.category_id == Category.category_id,
        )
        .where(
            Transaction.user_id == user_id,
            Category.type == "expense",
            Transaction.transaction_at >= start_date,
            Transaction.transaction_at < end_date,
        )
        .group_by(
            Category.category_id,
            Category.name,
        )
        .order_by(
            func.sum(Transaction.amount).desc()
        )
    )

    return db.execute(statement).all()


def get_cashflow_for_range(
    db: Session,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    granularity: str,
) -> list:
    if granularity == "day":
        bucket = func.date_trunc(
            "day",
            Transaction.transaction_at,
        )

    elif granularity == "week":
        bucket = func.date_trunc(
            "week",
            Transaction.transaction_at,
        )

    else:
        bucket = func.date_trunc(
            "month",
            Transaction.transaction_at,
        )

    statement = (
        select(
            bucket.label("period_start"),
            Category.type,
            func.sum(Transaction.amount).label("amount"),
        )
        .join(
            Category,
            Category.category_id == Transaction.category_id,
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_at >= start_date,
            Transaction.transaction_at < end_date,
        )
        .group_by(
            bucket,
            Category.type,
        )
        .order_by(bucket)
    )

    return db.execute(statement).all()


def get_top_categories_for_range(
    db: Session,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
) -> list:
    statement = (
        select(
            Category.category_id,
            Category.name,
            Category.icon,
            func.count(Transaction.transaction_id).label("transaction_count"),
            func.sum(Transaction.amount).label("spent"),
        )
        .join(
            Transaction,
            Transaction.category_id == Category.category_id,
        )
        .where(
            Transaction.user_id == user_id,
            Category.type == "expense",
            Transaction.transaction_at >= start_date,
            Transaction.transaction_at < end_date,
        )
        .group_by(
            Category.category_id,
            Category.name,
            Category.icon,
        )
        .order_by(
            func.sum(Transaction.amount).desc()
        )
    )

    return db.execute(statement).all()