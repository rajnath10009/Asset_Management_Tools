from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, create_engine, SQLModel, select
from typing import List, Optional
from datetime import datetime
from model import Notification
from model import Employee

# Create a FastAPI app
app = FastAPI()

# Database URL (replace with your database configuration)
DATABASE_URL =  "mysql://root:446688@localhost/asset_management"  # Use your database connection URL here
engine = create_engine(DATABASE_URL)

# Pydantic models for validation

class NotificationBase(BaseModel):
    sender_id: int
    recipient_id: int
    message: str
    priority: int

class Notification1(BaseModel):    
    recipient_id: int
    message: str

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(Notification1):
    notification_id: int
    sent_at: datetime

    class Config:
        from_attributes = True

# Dependency to get the database session
def get_session():
    with Session(engine) as session:
        yield session

# User GET endpoint to retrieve notifications by employee ID (recipient_id)
@app.get("/user/notifications/", response_model=List[NotificationResponse])
def get_user_notifications(
    employee_id: int,  # Employee ID is required
    session: Session = Depends(get_session)
):
    # Check if the employee exists and if they are not an admin
    employee = session.exec(select(Employee).where(Employee.employee_id == employee_id)).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee does not exist")
    
    if employee.is_admin:
        raise HTTPException(status_code=403, detail="Access denied: Users cannot access this endpoint")

    # Fetch notifications for the specific employee as recipient
    query = select(Notification).where(Notification.recipient_id == employee_id).order_by(Notification.sent_at.desc())
    notifications = session.exec(query).all()

    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications found for the employee")
    
    return notifications

@app.get("/admin/notifications/", response_model=List[NotificationResponse])
def get_admin_notifications(
    user_id: int,  # User ID is required to determine admin or not
    session: Session = Depends(get_session)
):
    # Validate if the user is an admin by querying the Employee table
    employee = session.exec(select(Employee).where(Employee.employee_id == user_id)).first()
    if not employee:
        raise HTTPException(status_code=404, detail="User not found")

    if employee.is_admin:  # Check if the user is an admin
        # Fetch notifications sent specifically to the admin
        query = select(Notification).where(Notification.recipient_id == user_id).order_by(Notification.sent_at.desc())
        notifications = session.exec(query).all()
        if not notifications:
            raise HTTPException(status_code=404, detail="No notifications found for admin")
        return notifications
    else:
        # Fetch notifications excluding those sent to the admin
        raise HTTPException(status_code=403, detail="Access denied: Admin cannot access this endpoint")


# @app.get("/notifications/", response_model=List[NotificationResponse])
# def get_notifications(
#     user_id: int,  # User ID is required (either employee or admin)
#     session: Session = Depends(get_session)
# ):
#     # Fetch the user (employee or admin) from the database
#     user = session.exec(select(Employee).where(Employee.employee_id == user_id)).first()

#     if not user:
#         raise HTTPException(status_code=404, detail="User does not exist")

#     # Fetch notifications based on the user type
#     query = (
#         select(Notification)
#         .where(Notification.recipient_id == user_id)
#         .order_by(Notification.sent_at.desc())
#     )
#     notifications = session.exec(query).all()

#     if not notifications:
#         detail = "No notifications found for admin" if user.is_admin else "No notifications found for the employee"
#         raise HTTPException(status_code=404, detail=detail)

#     return notifications

