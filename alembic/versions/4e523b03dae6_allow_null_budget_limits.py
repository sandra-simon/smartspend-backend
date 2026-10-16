"""allow null budget limits

Revision ID: 4e523b03dae6
Revises: 05471e19b8da
Create Date: 2026-10-16 07:32:18.325115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e523b03dae6'
down_revision: Union[str, Sequence[str], None] = '05471e19b8da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.alter_column(
        "budgets",
        "limit_amount",
        existing_type=sa.Numeric(precision=12, scale=2),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "budgets",
        "limit_amount",
        existing_type=sa.Numeric(precision=12, scale=2),
        nullable=False,
    )