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
    # 1. Add columns matching models.py naming
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.add_column('users', sa.Column('password_hash', sa.String(), nullable=True))

    # 2. Add unique constraint after email column creation
    op.create_unique_constraint('uq_users_email', 'users', ['email'])


def downgrade() -> None:
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'email')
