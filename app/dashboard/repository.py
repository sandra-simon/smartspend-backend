from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.categories.model import Category
from app.transactions.model import Transaction

def transaction_time_ist():
    return Transaction.transaction_at.op("AT TIME ZONE")(
        "Asia/Kolkata"
    )

def get_monthly_totals(
    db: Session,
    user_id: int,
    year: int,
    month: int,
) -> tuple:
    transaction_ist = transaction_time_ist()
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
            func.extract("year", transaction_ist) == year,
            func.extract("month", transaction_ist) == month,
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


def has_monthly_transactions(
    db: Session,
    user_id: int,
    year: int,
    month: int,
) -> bool:
    transaction_ist = transaction_time_ist()
    statement = (
        select(Transaction.transaction_id)
        .where(
            Transaction.user_id == user_id,
            func.extract("year", transaction_ist) == year,
            func.extract("month", transaction_ist) == month,
        )
        .limit(1)
    )

    return db.execute(statement).first() is not None


def get_monthly_expense_breakdown(
    db: Session,
    user_id: int,
    year: int,
    month: int,
) -> list:
    transaction_ist = transaction_time_ist()
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
            func.extract("year", transaction_ist) == year,
            func.extract("month", transaction_ist) == month,
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