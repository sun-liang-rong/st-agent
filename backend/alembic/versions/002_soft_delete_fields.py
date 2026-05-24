"""add soft delete fields to chat_histories

Revision ID: 002_soft_delete
Revises: 001_initial
Create Date: 2026-05-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_soft_delete'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chat_histories', sa.Column('is_deleted', sa.Boolean(), server_default='0', nullable=False))
    op.add_column('chat_histories', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.create_index('ix_chat_histories_is_deleted', 'chat_histories', ['is_deleted'])


def downgrade() -> None:
    op.drop_index('ix_chat_histories_is_deleted', table_name='chat_histories')
    op.drop_column('chat_histories', 'deleted_at')
    op.drop_column('chat_histories', 'is_deleted')