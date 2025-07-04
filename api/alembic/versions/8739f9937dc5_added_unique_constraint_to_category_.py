"""Added unique constraint to category name and user_id combined

Revision ID: 8739f9937dc5
Revises: 
Create Date: 2025-07-04 13:50:17.708416
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '8739f9937dc5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraint on (user_id, category_name) in categories table."""
    op.create_unique_constraint(
        constraint_name="uix_user_category_name",
        table_name="categories",
        columns=["user_id", "category_name"]
    )


def downgrade() -> None:
    """Remove unique constraint on (user_id, category_name) in categories table."""
    op.drop_constraint(
        constraint_name="uix_user_category_name",
        table_name="categories",
        type_="unique"
    )
