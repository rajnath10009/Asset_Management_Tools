"""Create  notification

Revision ID: d54454cffd47
Revises: a07d7cbce890
Create Date: 2025-01-20 11:17:10.476991

"""
from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'd54454cffd47'
down_revision: Union[str, None] = 'a07d7cbce890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.alter_column('notification', 'priority',
               existing_type=mysql.INTEGER(),
               type_=sqlmodel.sql.sqltypes.AutoString(length=50),
               existing_nullable=False)
    op.drop_index('message', table_name='notification')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('message', 'notification', ['message'], unique=True)
    op.alter_column('notification', 'priority',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=50),
               type_=mysql.INTEGER(),
               existing_nullable=False)
    op.drop_table('Ticket')
    # ### end Alembic commands ###
