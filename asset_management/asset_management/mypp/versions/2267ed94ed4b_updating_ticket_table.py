"""updating ticket table

Revision ID: 2267ed94ed4b
Revises: 7077fcc18e10
Create Date: 2025-01-15 23:02:24.656391

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '2267ed94ed4b'
down_revision: Union[str, None] = '7077fcc18e10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
   # Remove the foreign key constraint
    op.drop_constraint('fk_Ticket_ticket_status_notification_id', 'ticket', type_='foreignkey')
    op.alter_column('ticket', 'ticket_status',
                    type_=sa.String(255),  # Changing column type to String (VARCHAR)
                    existing_type=sa.Integer(),  # Existing column type is Integer
                    nullable=True)  # Optionally make it nullable

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ticket', 'ticket_status',
                    type_=sa.Integer(),  # Revert to Integer
                    existing_type=sa.String(255),  # Existing column type is String
                    nullable=True)  # Make sure to maintain the nullable property if needed
    op.create_foreign_key(
        'tk_Ticket_ticket_status_notification_id',  # Name of the foreign key
        'ticket',                                  # Source table
        'notification',                            # Target table
        ['ticket_status'],                         # Source column(s)
        ['notification_id']                        # Target column(s)
    )
    # ### end Alembic commands ###
