# from fastapi import FastAPI, HTTPException
# from sqlmodel import SQLModel, Session, select, create_engine
# from typing import List, Optional
# from datetime import datetime
# from model import Ticket

# # Database setup
# DATABASE_URL = "mysql://root:446688@localhost/asset_management"
# engine = create_engine(DATABASE_URL, echo=True)

# # FastAPI instance
# app = FastAPI()

# # Ticket model (Pydantic class for requests and responses)
# class TicketBase(SQLModel):
#     employee_id: Optional[int]
#     asset_id: Optional[int]
#     ticket_type: str
#     ticket_status: Optional[int]
#     returned_condition: Optional[str]
#     raised_at: Optional[datetime] = None
#     resolved_at: Optional[datetime] = None

# class TicketCreate(TicketBase):
#     pass

# class TicketUpdate(SQLModel):
#     ticket_type: Optional[str]
#     ticket_status: Optional[int]
#     returned_condition: Optional[str]
#     resolved_at: Optional[datetime]

# class TicketRead(TicketBase):
#     ticket_id: int

# # Routes
# @app.post("/tickets/", response_model=TicketRead)
# def create_ticket(ticket: TicketCreate):
#     with Session(engine) as session:
#         db_ticket = Ticket.from_orm(ticket)
#         session.add(db_ticket)
#         session.commit()
#         session.refresh(db_ticket)
#         return db_ticket

# @app.get("/tickets/", response_model=List[TicketRead])
# def read_tickets(skip: int = 0, limit: int = 10):
#     with Session(engine) as session:
#         tickets = session.exec(select(Ticket).offset(skip).limit(limit)).all()
#         return tickets

# @app.get("/tickets/{ticket_id}", response_model=TicketRead)
# def read_ticket(ticket_id: int):
#     with Session(engine) as session:
#         ticket = session.get(Ticket, ticket_id)
#         if not ticket:
#             raise HTTPException(status_code=404, detail="Ticket not found")
#         return ticket

# @app.patch("/tickets/{ticket_id}", response_model=TicketRead)
# def update_ticket(ticket_id: int, ticket_update: TicketUpdate):
#     with Session(engine) as session:
#         db_ticket = session.get(Ticket, ticket_id)
#         if not db_ticket:
#             raise HTTPException(status_code=404, detail="Ticket not found")

#         ticket_data = ticket_update.dict(exclude_unset=True)
#         for key, value in ticket_data.items():
#             setattr(db_ticket, key, value)

#         session.add(db_ticket)
#         session.commit()
#         session.refresh(db_ticket)
#         return db_ticket

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, create_engine
from typing import Optional, Literal
from datetime import datetime
from model import Ticket, Notification

# Database configuration
DATABASE_URL = "mysql://root:446688@localhost/asset_management"  # Replace with your actual database URL
engine = create_engine(DATABASE_URL)

# FastAPI app initialization
app = FastAPI()

# Pydantic models for Ticket
class TicketBase(BaseModel):
    employee_id: int
    asset_id: Optional[int]
    ticket_type: Literal["request", "return", "maintenance"]  # Restrict input to specific values
    ticket_status: Literal["open", "pending", "closed"]       # Restrict input to specific values

class TicketCreate(TicketBase):
    pass

class TicketResponse(TicketBase):
    ticket_id: int
    raised_at: datetime

    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    sender_id: int
    recipient_id: int
    message: str
    priority: int
    

class NotificationInst(NotificationBase):
    notification_id: int
    sent_at: datetime


# Dependency to get the database session
def get_session():
    with Session(engine) as session:
        yield session

# POST endpoint to create a ticket and a notification
# this comment is to test the git push command
@app.post("/tickets/", response_model=TicketResponse)
def create_ticket(ticket: TicketCreate, session: Session = Depends(get_session)):
    # Create the ticket
    db_ticket = Ticket(**ticket.dict())
    session.add(db_ticket)
    session.commit()
    session.refresh(db_ticket)

    # Create the corresponding notification
    notification_message = f"A {ticket.ticket_type} ticket has been closed with status {ticket.ticket_status}."
    db_notification = Notification(
        sender_id=ticket.employee_id,  # Assuming the employee is the sender
        recipient_id=9,  # Assign to an admin or relevant recipient
        message=notification_message,
        priority=1,
        sent_at=datetime.utcnow()
    )
    session.add(db_notification)
    session.commit()
    session.refresh(db_notification)

    return db_ticket

