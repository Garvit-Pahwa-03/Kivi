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
    # 1. Add the missing column first
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))

    # 2. Add the unique constraint AFTER the column exists
    op.create_unique_constraint('uq_users_email', 'users', ['email'])


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_email', type_='unique')
