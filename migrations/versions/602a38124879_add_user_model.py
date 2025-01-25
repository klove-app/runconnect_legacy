"""Add User model

Revision ID: 602a38124879
Revises: 
Create Date: 2025-01-08 11:43:59.408100

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '602a38124879'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('goal_km', sa.Float(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###