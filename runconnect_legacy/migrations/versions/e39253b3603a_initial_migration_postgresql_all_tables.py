"""initial_migration_postgresql_all_tables

Revision ID: e39253b3603a
Revises: fbc4fc0051a7
Create Date: 2025-01-24 17:33:53.530681

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e39253b3603a'
down_revision: Union[str, None] = 'fbc4fc0051a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('challenges',
    sa.Column('challenge_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('goal_km', sa.Float(), nullable=True),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('chat_id', sa.String(length=255), nullable=True),
    sa.Column('is_system', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('challenge_id')
    )
    op.create_index(op.f('ix_challenges_challenge_id'), 'challenges', ['challenge_id'], unique=False)
    op.create_table('group_goals',
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('total_goal', sa.Float(), nullable=True),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.PrimaryKeyConstraint('year')
    )
    op.create_table('teams',
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.Column('team_name', sa.String(length=255), nullable=True),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('team_id')
    )
    op.create_index(op.f('ix_teams_team_id'), 'teams', ['team_id'], unique=False)
    op.create_table('yearly_archive',
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('yearly_goal', sa.Float(), nullable=True),
    sa.Column('yearly_progress', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('year', 'user_id')
    )
    op.create_table('challenge_participants',
    sa.Column('challenge_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=255), nullable=False),
    sa.Column('progress', sa.Float(), nullable=True),
    sa.Column('joined_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['challenge_id'], ['challenges.challenge_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('challenge_id', 'user_id')
    )
    op.create_table('team_members',
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=255), nullable=False),
    sa.Column('joined_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['team_id'], ['teams.team_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('team_id', 'user_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('team_members')
    op.drop_table('challenge_participants')
    op.drop_table('yearly_archive')
    op.drop_index(op.f('ix_teams_team_id'), table_name='teams')
    op.drop_table('teams')
    op.drop_table('group_goals')
    op.drop_index(op.f('ix_challenges_challenge_id'), table_name='challenges')
    op.drop_table('challenges')
    # ### end Alembic commands ###