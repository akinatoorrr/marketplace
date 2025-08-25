"""create gin index concurrently idx_post_tsv

Revision ID: 69be59971e5b
Revises: a4d0f10a5f29
Create Date: 2025-08-25 07:36:06.466307

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69be59971e5b'
down_revision: Union[str, Sequence[str], None] = 'a4d0f10a5f29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.get_context().autocommit_block():
        op.create_index(
            'idx_post_tsv',
            'post',
            ['tsv'],
            unique=False,
            postgresql_using='gin',
            postgresql_concurrently=True
        )


def downgrade():
    with op.get_context().autocommit_block():
        op.drop_index('idx_post_tsv', table_name='post', postgresql_concurrently=True)
