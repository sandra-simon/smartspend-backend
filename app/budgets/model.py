from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    budget_id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.category_id"),
        nullable=False,
        index=True,
    )

    year: Mapped[int] = mapped_column(
        nullable=False,
    )

    month: Mapped[int] = mapped_column(
        nullable=False,
    )

    limit_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "year",
            "month",
            name="uq_budget_category_year_month",
        ),
    )