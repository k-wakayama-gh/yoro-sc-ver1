"""change column name of userchild table

Revision ID: 94d5d4ca5cb3
Revises: bee4622fc4b0
Create Date: 2024-03-29 14:59:30.587819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '94d5d4ca5cb3'
down_revision: Union[str, None] = 'bee4622fc4b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("userchild", "first_name", new_column_name="child_first_name")
    op.alter_column("userchild", "last_name", new_column_name="child_last_name")
    op.alter_column("userchild", "first_name_furigana", new_column_name="child_first_name_furigana")
    op.alter_column("userchild", "last_name_furigana", new_column_name="child_last_name_furigana")


def downgrade() -> None:
    pass
