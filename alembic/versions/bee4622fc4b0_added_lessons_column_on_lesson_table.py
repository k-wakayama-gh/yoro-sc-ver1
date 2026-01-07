"""added lessons column on lesson table

Revision ID: bee4622fc4b0
Revises: 812fb31b777a
Create Date: 2024-03-18 14:12:02.523569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'bee4622fc4b0'
down_revision: Union[str, None] = '812fb31b777a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
