from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Session, select, create_engine,Field
from typing import List, Optional
from datetime import datetime
from test1 import Ticket
from enum import Enum
import pytz
import logging
from sqlalchemy.exc import SQLAlchemyError




# Database setup
DATABASE_URL = "mysql://root:qwerty111@localhost/proj"
engine = create_engine(DATABASE_URL, echo=True)


# FastAPI instance
app = FastAPI()


# Enum with string values
class TicketStatusEnum(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class PriorityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class TickettypeEnum(str, Enum):
    REQUEST = "REQUEST"
    MAINTENANCE= "MAINTENANCE"
    RETURN = "RETURN"

# Timezone setup (use your local timezone)
local_timezone = pytz.timezone('Asia/Kolkata')

# Ticket model (Pydantic class for requests and responses)
class TicketBase(SQLModel):
    employee_id: Optional[int]
    asset_id: Optional[int]
    ticket_type: Optional[TickettypeEnum]
    ticket_status: Optional[TicketStatusEnum]
    returned_condition: Optional[str]
    raised_at: Optional[datetime] = None
    #resolved_at: Optional[datetime] = None
    priority: Optional[PriorityEnum]# Default priority is LOW


class TicketCreate(TicketBase):
    pass


class TicketUpdate(SQLModel):
    ticket_type: Optional[TickettypeEnum]
    ticket_status: Optional[TicketStatusEnum]
    returned_condition: Optional[str]
    resolved_at: Optional[datetime]
    priority: Optional[PriorityEnum] = PriorityEnum.LOW   # String priority (example: 'LOW', 'MEDIUM', 'HIGH')
 
class TicketRead(TicketBase):
    ticket_id: int
    priority: PriorityEnum

 
# Routes
@app.post("/tickets/", response_model=TicketRead)
def create_ticket(ticket: TicketCreate):

    with Session(engine) as session:
        # Initialize the db_ticket from the ORM model
        db_ticket = Ticket(**ticket.dict())
        #db_ticket = Ticket.from_orm(ticket)

        # Set the raised_at to current local time
        if db_ticket.raised_at is None:
            db_ticket.raised_at = datetime.now(local_timezone)

        db_ticket.resolved_at =  None
        
        # Ensure priority is set if not provided
        if db_ticket.priority is None:
            db_ticket.priority = PriorityEnum.LOW 

        session.add(db_ticket)
        session.commit()
        session.refresh(db_ticket)
        return db_ticket
        




@app.get("/tickets/{ticket_id}", response_model=TicketRead)
def read_ticket(ticket_id: int):
    with Session(engine) as session:
        ticket = session.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket



@app.put("/tickets/{ticket_id}", response_model=TicketRead)
def update_ticket(ticket_id: int, ticket_update: TicketUpdate):
    with Session(engine) as session:
        # Fetch the ticket from the database
        db_ticket = session.get(Ticket, ticket_id)


        # If the ticket doesn't exist, raise a 404 error
        if not db_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
         # Check if the ticket status is being changed to 'closed' and update resolved_at
        if  ticket_update.ticket_status == "CLOSED":
            
            db_ticket.resolved_at = datetime.utcnow()  # Set the resolved_at timestamp

        # Update the ticket with new values from the request
        if ticket_update.ticket_type:
            db_ticket.ticket_type = ticket_update.ticket_type
        if ticket_update.ticket_status:
            db_ticket.ticket_status = ticket_update.ticket_status
        if ticket_update.returned_condition:
            db_ticket.returned_condition = ticket_update.returned_condition
        # if ticket_update.resolved_at:
        #     db_ticket.resolved_at = ticket_update.resolved_at
        if ticket_update.priority:
            db_ticket.priority = ticket_update.priority  # Update priority field if present

        # Commit the changes to the database
        session.commit()

        # Return the updated ticket
        session.refresh(db_ticket)
        return db_ticket



