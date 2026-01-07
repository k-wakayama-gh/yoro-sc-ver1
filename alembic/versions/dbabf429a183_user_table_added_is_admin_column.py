"""user table added is_admin column

Revision ID: dbabf429a183
Revises: 94d5d4ca5cb3
Create Date: 2024-04-03 14:32:36.116339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'dbabf429a183'
down_revision: Union[str, None] = '94d5d4ca5cb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user", sa.Column("is_admin", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("user", "is_admin")

