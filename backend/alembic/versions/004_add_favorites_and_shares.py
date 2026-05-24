"""add image_favorites and shares tables

Revision ID: 004_favorites_shares
Revises: 003_avatar
Create Date: 2026-05-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '004_favorites_shares'
down_revision: Union[str, None] = '003_avatar'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # image_favorites table
    op.create_table(
        'image_favorites',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(512), nullable=False),
        sa.Column('prompt', sa.String(1000), nullable=True),
        sa.Column('style', sa.String(50), nullable=True),
        sa.Column('ratio', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_image_favorites_user_id', 'image_favorites', ['user_id'])

    # shares table
    op.create_table(
        'shares',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('content_id', sa.String(64), nullable=False),
        sa.Column('token', sa.String(64), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('view_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('token'),
    )
    op.create_index('ix_shares_user_id', 'shares', ['user_id'])
    op.create_index('ix_shares_token', 'shares', ['token'])


def downgrade() -> None:
    op.drop_index('ix_shares_token', table_name='shares')
    op.drop_index('ix_shares_user_id', table_name='shares')
    op.drop_table('shares')
    op.drop_index('ix_image_favorites_user_id', table_name='image_favorites')
    op.drop_table('image_favorites')
