"""fix_password_hash_column_name

Revision ID: 8113858dec41
Revises: 08dd4d1ac5ea
Create Date: 2026-09-14 21:30:57.523902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8113858dec41'
down_revision: Union[str, None] = '08dd4d1ac5ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add password_hash if it was missed
    op.add_column('users', sa.Column('password_hash', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'password_hash')
