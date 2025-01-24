"""add subscription tables

Revision ID: add_subscription_tables
Revises: 7f1deaa475c2
Create Date: 2024-01-24 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_subscription_tables'
down_revision = '7f1deaa475c2'
branch_labels = None
depends_on = None

def upgrade():
    # Создаем таблицу тарифных планов
    op.create_table('subscription_plans',
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('plan_id')
    )

    # Создаем таблицу возможностей тарифных планов
    op.create_table('subscription_features',
        sa.Column('feature_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('feature_type', sa.String(50), nullable=False),  # boolean, numeric, text
        sa.Column('value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),  # Значение возможности (true/false, число, текст)
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.plan_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('feature_id')
    )

    # Создаем таблицу подписок пользователей
    op.create_table('user_subscriptions',
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('payment_id', sa.String(255), nullable=True),  # ID платежа во внешней системе
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.plan_id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('subscription_id')
    )

    # Добавляем индексы для оптимизации запросов
    op.create_index('ix_user_subscriptions_user_id', 'user_subscriptions', ['user_id'])
    op.create_index('ix_user_subscriptions_plan_id', 'user_subscriptions', ['plan_id'])
    op.create_index('ix_subscription_features_plan_id', 'subscription_features', ['plan_id'])

def downgrade():
    op.drop_index('ix_subscription_features_plan_id')
    op.drop_index('ix_user_subscriptions_plan_id')
    op.drop_index('ix_user_subscriptions_user_id')
    op.drop_table('user_subscriptions')
    op.drop_table('subscription_features')
    op.drop_table('subscription_plans') 