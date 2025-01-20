from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Pydantic Models

'''class TicketBase(BaseModel):
    employee_id: Optional[int]
    asset_id: Optional[int]
    ticket_type: str
    ticket_status: Optional[int]
    returned_condition: Optional[str]
    raised_at: Optional[datetime]
    resolved_at: Optional[datetime]'''

class TicketCreate(BaseModel):
    ticket_id : int
    employee_id: int
    asset_id : int
    ticket_type: str  # Required when creating a new ticket
    ticket_status: Optional[int]
    returned_condition: Optional[str]
    raised_at: Optional[datetime]
    resolved_at: Optional[datetime]

'''class TicketUpdate(TicketBase):
    pass

# class Ticket(TicketBase):
#     ticket_id: int

class Config:
    from_attributes = True'''
