"""Create  ticket2

Revision ID: 67dd97590681
Revises: d54454cffd47
Create Date: 2025-01-20 11:19:30.115199

"""
from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67dd97590681'
down_revision: Union[str, None] = 'd54454cffd47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Ticket',
    sa.Column('ticket_id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=True),
    sa.Column('asset_id', sa.Integer(), nullable=True),
    sa.Column('ticket_type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('ticket_status', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('raised_at', sa.DateTime(), nullable=True),
    sa.Column('resolved_at', sa.DateTime(), nullable=True),
    sa.Column('priority', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.ForeignKeyConstraint(['asset_id'], ['asset.asset_id'], ),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.employee_id'], ),
    sa.PrimaryKeyConstraint('ticket_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Ticket')
    # ### end Alembic commands ###
