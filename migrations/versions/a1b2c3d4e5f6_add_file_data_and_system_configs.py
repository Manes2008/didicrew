"""add_file_data_and_system_configs

Revision ID: a1b2c3d4e5f6
Revises: 4246330d6fdd
Create Date: 2026-08-03 16:31:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '4246330d6fdd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_cols = [c['name'] for c in inspector.get_columns('media_files')]
    if 'file_data' not in existing_cols:
        op.add_column('media_files', sa.Column('file_data', sa.LargeBinary(), nullable=True))
    existing_tables = inspector.get_table_names()
    if 'system_configs' not in existing_tables:
        op.create_table(
            'system_configs',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('key', sa.String(length=100), nullable=False),
            sa.Column('value', sa.Text(), nullable=True),
            sa.Column('is_encrypted', sa.Boolean(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('key')
        )


def downgrade() -> None:
    op.drop_column('media_files', 'file_data')
    op.drop_table('system_configs')
