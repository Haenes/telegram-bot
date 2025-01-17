"""Init migration.

Revision ID: fd251009fb33
Revises: 
Create Date: 2025-01-11 03:22:32.971594+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd251009fb33'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tg_user',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('user_token', sa.VARCHAR(length=255), nullable=False),
    sa.Column('language', sa.VARCHAR(length=7), nullable=True),
    sa.Column('timezone', sa.VARCHAR(length=30), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('user_id'),
    sa.UniqueConstraint('user_token')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tg_user')
    # ### end Alembic commands ###
