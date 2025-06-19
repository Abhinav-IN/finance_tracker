"""Added unique constraints for attributes of user

Revision ID: 9b2fc502beee
Revises: 
Create Date: 2025-06-17 15:46:48.231012
"""

from typing import Sequence, Union

from alembic import op




# revision identifiers, used by Alembic.
revision: str = '9b2fc502beee'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    op.create_unique_constraint('uq_users_username', 'users', ['username'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.drop_constraint('uq_users_username', 'users', type_='unique')
