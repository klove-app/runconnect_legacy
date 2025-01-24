"""remove yearly_progress column

Revision ID: remove_yearly_progress_column
Revises: 7f1deaa475c2
Create Date: 2024-01-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'remove_yearly_progress_column'
down_revision = '7f1deaa475c2'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'yearly_progress')
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('yearly_progress', sa.Float(), nullable=True))
    # ### end Alembic commands ### 