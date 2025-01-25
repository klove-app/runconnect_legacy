"""new_db_structure

Revision ID: new_db_structure
Revises: e39253b3603a
Create Date: 2024-01-24 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'new_db_structure'
down_revision = 'e39253b3603a'
branch_labels = None
depends_on = None


def upgrade():
    # Создаем новые таблицы
    
    # Тарифы и подписки
    op.create_table(
        'subscription_plans',
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Decimal(), nullable=False),
        sa.Column('billing_period', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP()),
        sa.PrimaryKeyConstraint('plan_id')
    )

    op.create_table(
        'plan_features',
        sa.Column('feature_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('feature_key', sa.String(100), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('feature_id'),
        sa.UniqueConstraint('feature_key')
    )

    op.create_table(
        'plan_feature_relations',
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('feature_id', sa.Integer(), nullable=False),
        sa.Column('feature_limit', JSONB()),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.plan_id']),
        sa.ForeignKeyConstraint(['feature_id'], ['plan_features.feature_id']),
        sa.PrimaryKeyConstraint('plan_id', 'feature_id')
    )

    op.create_table(
        'user_subscriptions',
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.TIMESTAMP(), nullable=False),
        sa.Column('end_date', sa.TIMESTAMP(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('payment_status', sa.String(50)),
        sa.Column('auto_renewal', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP()),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.plan_id']),
        sa.PrimaryKeyConstraint('user_id', 'plan_id', 'start_date')
    )

    # Планы тренировок
    op.create_table(
        'training_templates',
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('difficulty_level', sa.String(50)),
        sa.Column('target_metrics', JSONB()),
        sa.Column('instructions', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('template_id')
    )

    op.create_table(
        'training_plans',
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('generation_params', JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP()),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('plan_id')
    )

    op.create_table(
        'scheduled_trainings',
        sa.Column('training_id', sa.BigInteger(), nullable=False),
        sa.Column('plan_id', sa.Integer()),
        sa.Column('template_id', sa.Integer()),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('target_metrics', JSONB()),
        sa.Column('completed_activity_id', sa.BigInteger()),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP()),
        sa.ForeignKeyConstraint(['plan_id'], ['training_plans.plan_id']),
        sa.ForeignKeyConstraint(['template_id'], ['training_templates.template_id']),
        sa.ForeignKeyConstraint(['completed_activity_id'], ['running_log.log_id']),
        sa.PrimaryKeyConstraint('training_id')
    )

    # Интеграции
    op.create_table(
        'user_integrations',
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('service_name', sa.String(50), nullable=False),
        sa.Column('service_user_id', sa.String(255)),
        sa.Column('access_token', sa.Text()),
        sa.Column('refresh_token', sa.Text()),
        sa.Column('token_expires_at', sa.TIMESTAMP()),
        sa.Column('last_sync_at', sa.TIMESTAMP()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP()),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('user_id', 'service_name')
    )

    # Аналитика тренировок
    op.create_table(
        'user_training_progress',
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('training_load', sa.Decimal()),
        sa.Column('fitness_level', sa.Decimal()),
        sa.Column('fatigue_level', sa.Decimal()),
        sa.Column('form_score', sa.Decimal()),
        sa.Column('vo2max_estimate', sa.Decimal()),
        sa.Column('updated_at', sa.TIMESTAMP()),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('user_id', 'date')
    )

    op.create_table(
        'training_recommendations',
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('recommended_load', JSONB()),
        sa.Column('recommended_activities', JSONB()),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('user_id', 'date')
    )

    # Добавляем новые колонки в существующие таблицы
    op.add_column('running_log', sa.Column('external_id', sa.String(255)))
    op.add_column('running_log', sa.Column('external_source', sa.String(50)))
    op.add_column('running_log', sa.Column('detailed_metrics', JSONB()))
    op.add_column('running_log', sa.Column('splits', JSONB()))
    op.add_column('running_log', sa.Column('elevation_data', JSONB()))
    op.add_column('running_log', sa.Column('average_heartrate', sa.Decimal()))
    op.add_column('running_log', sa.Column('max_heartrate', sa.Decimal()))
    op.add_column('running_log', sa.Column('perceived_effort', sa.Integer()))
    op.add_column('running_log', sa.Column('training_load', sa.Decimal()))
    op.add_column('running_log', sa.Column('recovery_time', sa.Interval()))

    # Создаем индексы
    op.create_index('idx_user_subscriptions_active', 'user_subscriptions', 
                    ['user_id', 'status'], 
                    postgresql_where=sa.text("status = 'active'"))
    
    op.create_index('idx_scheduled_trainings_user', 'scheduled_trainings',
                    ['plan_id', 'scheduled_date'])
    
    op.create_index('idx_user_integrations_active', 'user_integrations',
                    ['service_name', 'last_sync_at'],
                    postgresql_where=sa.text("is_active = true"))
    
    op.create_index('idx_activities_external', 'running_log',
                    ['external_source', 'external_id'])


def downgrade():
    # Удаляем индексы
    op.drop_index('idx_activities_external')
    op.drop_index('idx_user_integrations_active')
    op.drop_index('idx_scheduled_trainings_user')
    op.drop_index('idx_user_subscriptions_active')

    # Удаляем колонки из running_log
    op.drop_column('running_log', 'recovery_time')
    op.drop_column('running_log', 'training_load')
    op.drop_column('running_log', 'perceived_effort')
    op.drop_column('running_log', 'max_heartrate')
    op.drop_column('running_log', 'average_heartrate')
    op.drop_column('running_log', 'elevation_data')
    op.drop_column('running_log', 'splits')
    op.drop_column('running_log', 'detailed_metrics')
    op.drop_column('running_log', 'external_source')
    op.drop_column('running_log', 'external_id')

    # Удаляем таблицы в обратном порядке
    op.drop_table('training_recommendations')
    op.drop_table('user_training_progress')
    op.drop_table('user_integrations')
    op.drop_table('scheduled_trainings')
    op.drop_table('training_plans')
    op.drop_table('training_templates')
    op.drop_table('user_subscriptions')
    op.drop_table('plan_feature_relations')
    op.drop_table('plan_features')
    op.drop_table('subscription_plans') 