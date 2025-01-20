"""Create  notify

Revision ID: 320b6bd6bb4e
Revises: 67dd97590681
Create Date: 2025-01-20 11:55:53.847843

"""
from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '320b6bd6bb4e'
down_revision: Union[str, None] = '67dd97590681'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    op.drop_table('ticket')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ticket',
    sa.Column('ticket_id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('employee_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('asset_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ticket_type', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('ticket_status', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('raised_at', mysql.DATETIME(), nullable=True),
    sa.Column('resolved_at', mysql.DATETIME(), nullable=True),
    sa.Column('priority', mysql.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['asset_id'], ['asset.asset_id'], name='ticket_ibfk_1'),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.employee_id'], name='ticket_ibfk_2'),
    sa.PrimaryKeyConstraint('ticket_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('Ticket')
    # ### end Alembic commands ###
