from sqlalchemy import select
from sqlalchemy.orm import Session

from app.categories.model import Category
from app.budgets.model import Budget


def get_category_by_name(
    db: Session,
    user_id: int,
    name: str,
) -> Category | None:
    statement = select(Category).where(
        Category.user_id == user_id,
        Category.name == name,
    )

    return db.scalar(statement)


def create_category(
    db: Session,
    user_id: int,
    name: str,
    icon: str,
    type: str,
) -> Category:
    category = Category(
        user_id=user_id,
        name=name,
        icon=icon,
        type=type,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def get_categories(
    db: Session,
    user_id: int,
    category_type: str | None = None,
) -> list[Category]:
    statement = select(Category).where(
        Category.user_id == user_id
    )

    if category_type is not None:
        statement = statement.where(
            Category.type == category_type
        )

    statement = statement.order_by(
        Category.name.asc()
    )

    return list(db.scalars(statement).all())


def get_category_by_id(
    db: Session,
    user_id: int,
    category_id: int,
) -> Category | None:
    statement = select(Category).where(
        Category.category_id == category_id,
        Category.user_id == user_id,
    )
    return db.scalar(statement)


def update_category(
    db: Session,
    category: Category,
    name: str | None = None,
    icon: str | None = None,
    type: str | None = None,
) -> Category:
    if name is not None:
        category.name = name

    if icon is not None:
        category.icon = icon

    if type is not None:
        category.type = type

    db.commit()
    db.refresh(category)

    return category


def delete_category(
    db: Session,
    category: Category,
) -> None:
    db.delete(category)
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
            (
                Budget.year * 12 + Budget.month
            ) <= requested_period,
        )
        .order_by(
            Budget.year.desc(),
            Budget.month.desc(),
        )
        .limit(1)
    )

    return db.scalar(statement)