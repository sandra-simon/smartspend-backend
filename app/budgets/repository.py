from sqlalchemy import select, func
from sqlalchemy.orm import Session
from decimal import Decimal

from app.budgets.model import Budget
from app.transactions.model import Transaction

def get_budget(
    db: Session,
    category_id: int,
    year: int,
    month: int,
) -> Budget | None:
    statement = select(Budget).where(
        Budget.category_id == category_id,
        Budget.year == year,
        Budget.month == month,
    )

    return db.scalar(statement)


def create_budget(
    db: Session,
    category_id: int,
    year: int,
    month: int,
    limit_amount,
) -> Budget:
    budget = Budget(
        category_id=category_id,
        year=year,
        month=month,
        limit_amount=limit_amount,
    )

    db.add(budget)
    db.commit()
    db.refresh(budget)

    return budget


def update_budget(
    db: Session,
    budget: Budget,
    limit_amount,
) -> Budget:
    budget.limit_amount = limit_amount

    db.commit()
    db.refresh(budget)

    return budget


def delete_budget(
    db: Session,
    budget: Budget,
) -> None:
    db.delete(budget)
    db.commit()


def get_applicable_budget(
    db: Session,
    category_id: int,
    year: int,
    month: int,
) -> Budget | None:
    requested_period = year * 12 + month

    statement = (
        select(Budget)
        .where(
            Budget.category_id == category_id,
            (Budget.year * 12 + Budget.month) <= requested_period,
        )
        .order_by(
            Budget.year.desc(),
            Budget.month.desc(),
        )
        .limit(1)
    )

    return db.scalar(statement)


def get_category_monthly_spent(
    db: Session,
    category_id: int,
    year: int,
    month: int,
) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(
            Transaction.category_id == category_id,
            func.extract("year", Transaction.transaction_at) == year,
            func.extract("month", Transaction.transaction_at) == month,
        )
    )

    return Decimal(str(total))


def delete_budgets_for_category(
    db: Session,
    category_id: int,
) -> None:
    budgets = db.scalars(
        select(Budget).where(
            Budget.category_id == category_id
        )
    ).all()

    for budget in budgets:
        db.delete(budget)

    db.commit()