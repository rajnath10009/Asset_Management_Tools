"""changed message in notification

Revision ID: f97a71e386d7
Revises: f462f9b23aab
Create Date: 2025-01-16 16:22:52.514521

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'f97a71e386d7'
down_revision: Union[str, None] = 'f462f9b23aab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('message', table_name='notification')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('message', 'notification', ['message'], unique=True)
    op.create_table('ticket',
    sa.Column('ticket_id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('employee_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('asset_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ticket_type', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('ticket_status', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('returned_condition', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('raised_at', mysql.DATETIME(), nullable=True),
    sa.Column('resolved_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['asset_id'], ['asset.asset_id'], name='ticket_ibfk_1'),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.employee_id'], name='ticket_ibfk_2'),
    sa.PrimaryKeyConstraint('ticket_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('Ticket')
    # ### end Alembic commands ###
