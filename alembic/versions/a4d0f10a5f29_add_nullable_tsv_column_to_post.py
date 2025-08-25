"""add nullable tsv column to post

Revision ID: a4d0f10a5f29
Revises: bac1ff2756d2
Create Date: 2025-08-25 07:22:13.572918

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a4d0f10a5f29'
down_revision: Union[str, Sequence[str], None] = 'bac1ff2756d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('post', sa.Column('tsv', postgresql.TSVECTOR(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('post', 'tsv')
