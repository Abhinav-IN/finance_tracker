"""Added budget amount attribute and its check constraint

Revision ID: 7c4db3959fc8
Revises: 8739f9937dc5
Create Date: 2025-07-04 19:11:32.505590
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7c4db3959fc8'
down_revision = '8739f9937dc5'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add 'budget_amount' column to 'budget' table
    op.add_column('budget', sa.Column('budget_amount', sa.Integer(), nullable=False))
    # Add check constraint: budget_amount > 0
    op.create_check_constraint(
        constraint_name='budget_amount_check',
        table_name='budget',
        condition=sa.text('budget_amount > 0')
    )

def downgrade() -> None:
    # Remove check constraint first
    op.drop_constraint('budget_amount_check', 'budget', type_='check')
    # Then remove column
    op.drop_column('budget', 'budget_amount')
