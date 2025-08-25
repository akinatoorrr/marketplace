"""drop old ix_post_tsv concurrently

Revision ID: abeeaa638622
Revises: 69be59971e5b
Create Date: 2025-08-25 07:38:12.157742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abeeaa638622'
down_revision: Union[str, Sequence[str], None] = '69be59971e5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_post_tsv;")


def downgrade():
    pass
