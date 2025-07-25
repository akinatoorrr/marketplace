from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'add_post_tsvector'
down_revision = '19b0b9c6850b'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем колонку для полнотекстового индекса
    op.add_column('post', sa.Column('tsv', postgresql.TSVECTOR(), nullable=True))

    # Создаем функцию обновления tsvector
    op.execute("""
    CREATE FUNCTION post_tsvector_update_trigger() RETURNS trigger AS $$
    BEGIN
      NEW.tsv :=
        setweight(to_tsvector('russian', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('russian', coalesce(NEW.text, '')), 'B');
      RETURN NEW;
    END
    $$ LANGUAGE plpgsql;
    """)

    # Создаем триггер, вызывающий функцию перед вставкой и обновлением
    op.execute("""
    CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
    ON post FOR EACH ROW EXECUTE FUNCTION post_tsvector_update_trigger();
    """)

    # Создаем GIN индекс по колонке tsv
    op.create_index('ix_post_tsv', 'post', ['tsv'], postgresql_using='gin')


def downgrade():
    op.drop_index('ix_post_tsv', table_name='post')
    op.execute("DROP TRIGGER IF EXISTS tsvectorupdate ON post;")
    op.execute("DROP FUNCTION IF EXISTS post_tsvector_update_trigger();")
    op.drop_column('post', 'tsv')
