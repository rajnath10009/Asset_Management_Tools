"""Create tables

Revision ID: c8c9af4f53aa
Revises: f3eae3f6d1f9
Create Date: 2025-01-17 21:55:13.045978

"""
from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c8c9af4f53aa'
down_revision: Union[str, None] = 'f3eae3f6d1f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_table('Ticket',
    # sa.Column('ticket_id', sa.Integer(), nullable=False),
    # sa.Column('employee_id', sa.Integer(), nullable=True),
    # sa.Column('asset_id', sa.Integer(), nullable=True),
    # sa.Column('ticket_type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    # sa.Column('ticket_status', sa.Integer(), nullable=True),
    # sa.Column('assigned_date', sa.DateTime(), nullable=True),
    # sa.Column('return_date', sa.DateTime(), nullable=True),
    # sa.Column('returned_condition', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    # sa.Column('raised_at', sa.DateTime(), nullable=True),
    # sa.Column('resolved_at', sa.DateTime(), nullable=True),
    # sa.ForeignKeyConstraint(['asset_id'], ['asset.asset_id'], ),
    # sa.ForeignKeyConstraint(['employee_id'], ['employee.employee_id'], ),
    # sa.ForeignKeyConstraint(['ticket_status'], ['notification.notification_id'], ),
    # sa.PrimaryKeyConstraint('ticket_id')
    # )
    # op.drop_table('ticket')
    op.alter_column('asset', 'asset_type',
               existing_type=mysql.VARCHAR(length=50),
               type_=sa.Enum('LAPTOP', 'MOUSE', 'MONITOR', 'SPEAKER', 'KEYBOARD', name='assettype'),
               existing_nullable=False)
    op.alter_column('asset', 'asset_sl_no',
               existing_type=mysql.VARCHAR(length=100),
               type_=sqlmodel.sql.sqltypes.AutoString(length=8),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('asset', 'asset_sl_no',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=8),
               type_=mysql.VARCHAR(length=100),
               existing_nullable=False)
    op.alter_column('asset', 'asset_type',
               existing_type=sa.Enum('LAPTOP', 'MOUSE', 'MONITOR', 'SPEAKER', 'KEYBOARD', name='assettype'),
               type_=mysql.VARCHAR(length=50),
               existing_nullable=False)
    op.create_table('ticket',
    sa.Column('ticket_id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('employee_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('asset_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ticket_type', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('ticket_status', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('assigned_date', mysql.DATETIME(), nullable=True),
    sa.Column('return_date', mysql.DATETIME(), nullable=True),
    sa.Column('returned_condition', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('raised_at', mysql.DATETIME(), nullable=True),
    sa.Column('resolved_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['asset_id'], ['asset.asset_id'], name='ticket_ibfk_1'),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.employee_id'], name='ticket_ibfk_2'),
    sa.ForeignKeyConstraint(['ticket_status'], ['notification.notification_id'], name='ticket_ibfk_3'),
    sa.PrimaryKeyConstraint('ticket_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('Ticket')
    # ### end Alembic commands ###
