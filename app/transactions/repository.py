_UNSET = object()

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Select, case, func, select
from sqlalchemy.orm import Session, selectinload

from app.transactions.model import Transaction
from app.categories.model import Category


def create_transaction(
    db: Session,
    user_id: int,
    category_id: int,
    amount,
    currency: str,
    title: str,
    transaction_at,
    merchant: str | None = None,
    notes: str | None = None,
) -> Transaction:
    transaction = Transaction(
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        currency=currency,
        title=title,
        transaction_at=transaction_at,
        merchant=merchant,
        notes=notes,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def get_transactions(
    db: Session,
    user_id: int,
    type: str | None = None,
    category_id: int | None = None,
    search: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort_by: str = "transaction_at",
    sort_order: str = "desc",
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[Transaction], int]:
    statement = (
        select(Transaction)
        .options(selectinload(Transaction.category))
        .join(Category, Category.category_id == Transaction.category_id)
        .where(Transaction.user_id == user_id)
    )

    count_statement = (
        select(func.count(Transaction.transaction_id))
        .join(Category, Category.category_id == Transaction.category_id)
        .where(Transaction.user_id == user_id)
    )

    if type is not None:
        statement = statement.where(Category.type == type)
        count_statement = count_statement.where(Category.type == type)

    if category_id is not None:
        statement = statement.where(
            Transaction.category_id == category_id
        )
        count_statement = count_statement.where(
            Transaction.category_id == category_id
        )

    if search:
        search_pattern = f"%{search}%"
        search_filter = (
            Transaction.title.ilike(search_pattern)
            | Transaction.merchant.ilike(search_pattern)
            | Transaction.notes.ilike(search_pattern)
        )

        statement = statement.where(search_filter)
        count_statement = count_statement.where(search_filter)

    if date_from is not None:
        statement = statement.where(
            Transaction.transaction_at >= date_from
        )
        count_statement = count_statement.where(
            Transaction.transaction_at >= date_from
        )

    if date_to is not None:
        statement = statement.where(
            Transaction.transaction_at <= date_to
        )
        count_statement = count_statement.where(
            Transaction.transaction_at <= date_to
        )

    sort_column = {
        "transaction_at": Transaction.transaction_at,
        "amount": Transaction.amount,
        "title": Transaction.title,
    }[sort_by]

    if sort_order == "asc":
        statement = statement.order_by(sort_column.asc())
    else:
        statement = statement.order_by(sort_column.desc())

    statement = statement.offset(offset).limit(limit)

    transactions = list(db.scalars(statement).all())
    total = db.scalar(count_statement) or 0

    return transactions, total


def get_transaction_by_id(
    db: Session,
    user_id: int,
    transaction_id: int,
) -> Transaction | None:
    statement = select(Transaction).where(
        Transaction.transaction_id == transaction_id,
        Transaction.user_id == user_id,
    )

    return db.scalar(statement)


def update_transaction(
    db: Session,
    transaction: Transaction,
    category_id=None,
    amount=None,
    currency=None,
    title=None,
    transaction_at=None,
    merchant=_UNSET,
    notes=_UNSET,
) -> Transaction:
    if category_id is not None:
        transaction.category_id = category_id

    if amount is not None:
        transaction.amount = amount

    if currency is not None:
        transaction.currency = currency

    if title is not None:
        transaction.title = title

    if transaction_at is not None:
        transaction.transaction_at = transaction_at

    if merchant is not _UNSET:
        transaction.merchant = merchant

    if notes is not _UNSET:
        transaction.notes = notes

    db.commit()
    db.refresh(transaction)

    return transaction


def get_daily_net_totals(
    db: Session,
    user_id: int,
    type: str | None = None,
    category_id: int | None = None,
    search: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[dict]:
    # Group timestamps by their calendar date in Indian Standard Time.
    date_expression = func.date(
        Transaction.transaction_at.op("AT TIME ZONE")(
            "Asia/Kolkata"
        )
    )

    income_total = func.coalesce(
        func.sum(
            case(
                (Category.type == "income", Transaction.amount),
                else_=0,
            )
        ),
        0,
    )

    expense_total = func.coalesce(
        func.sum(
            case(
                (Category.type == "expense", Transaction.amount),
                else_=0,
            )
        ),
        0,
    )

    statement = (
        select(
            date_expression.label("date"),
            income_total.label("income_total"),
            expense_total.label("expense_total"),
        )
        .join(
            Category,
            Category.category_id == Transaction.category_id,
        )
        .where(Transaction.user_id == user_id)
    )

    if type is not None:
        statement = statement.where(Category.type == type)

    if category_id is not None:
        statement = statement.where(
            Transaction.category_id == category_id
        )

    if search:
        search_pattern = f"%{search}%"
        search_filter = (
            Transaction.title.ilike(search_pattern)
            | Transaction.merchant.ilike(search_pattern)
            | Transaction.notes.ilike(search_pattern)
        )
        statement = statement.where(search_filter)

    if date_from is not None:
        statement = statement.where(
            Transaction.transaction_at >= date_from
        )

    if date_to is not None:
        statement = statement.where(
            Transaction.transaction_at <= date_to
        )

    statement = (
        statement
        .group_by(date_expression)
        .order_by(date_expression.desc())
    )

    rows = db.execute(statement).all()
    results = []

    for row in rows:
        income = Decimal(str(row.income_total))
        expense = Decimal(str(row.expense_total))

        results.append(
            {
                "date": row.date,
                "income_total": income,
                "expense_total": expense,
                "net_total": income - expense,
            }
        )

    return results


def delete_transaction(
    db: Session,
    transaction: Transaction,
) -> None:
    db.delete(transaction)
    db.commit()