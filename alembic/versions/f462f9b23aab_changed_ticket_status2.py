"""changed ticket_status2

Revision ID: f462f9b23aab
Revises: c4097616ee64
Create Date: 2025-01-15 22:53:37.359282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f462f9b23aab'
down_revision: Union[str, None] = 'c4097616ee64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Ticket',
    sa.Column('ticket_id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=True),
    sa.Column('asset_id', sa.Integer(), nullable=True),
    sa.Column('ticket_type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('ticket_status', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('returned_condition', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('raised_at', sa.DateTime(), nullable=True),
    sa.Column('resolved_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['asset_id'], ['asset.asset_id'], ),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.employee_id'], ),
    sa.PrimaryKeyConstraint('ticket_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Ticket')
    # ### end Alembic commands ###
