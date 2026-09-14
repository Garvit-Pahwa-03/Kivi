"""add auth fields to users

Revision ID: 08dd4d1ac5ea
Revises: 5037ceea9a50
Create Date: 2026-09-14 14:08:27.534452

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08dd4d1ac5ea'
down_revision: Union[str, None] = '5037ceea9a50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Columns already exist on disk from a prior partial run that crashed before
    # Alembic recorded success - only the unique constraint is still missing.
    # SQLite requires batch mode to add a constraint to an existing table.
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_users_email', ['email'])


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_email', type_='unique')
