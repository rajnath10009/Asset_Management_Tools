from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlmodel import Session as SQLSession, create_engine, select
from model import Employee,Asset,Notification
from datetime import datetime, timezone, timedelta
from typing import List
import jwt


app = FastAPI()

# Database connection 
DATABASE_URL = "mysql://root:446688@localhost/asset_management"
engine = create_engine(DATABASE_URL)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT secret and algorithm
SECRET_KEY = "yoursecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

# Notification Endpoints Integrated with JWT Authentication

@app.get("/notifications/", response_model=List[NotificationResponse])
def get_notifications(
    token: str = Query(..., description="JWT token for authentication"),
    session: Session = Depends(get_session),
):
    """
    Fetch notifications for the authenticated user based on their role (admin or employee).
    """
    # Decode the JWT token to get the user details
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    # Fetch the user from the database
    user = session.exec(select(Employee).where(Employee.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    # Fetch notifications based on user role
    if user.is_admin:
        # Admin: Fetch notifications sent to the admin
        query = select(Notification).where(Notification.recipient_id == user.employee_id).order_by(Notification.sent_at.desc())
    else:
        # Employee: Fetch notifications sent to the employee
        query = select(Notification).where(Notification.recipient_id == user.employee_id).order_by(Notification.sent_at.desc())

    notifications = session.exec(query).all()

    if not notifications:
        detail = "No notifications found for admin" if user.is_admin else "No notifications found for the employee"
        raise HTTPException(status_code=404, detail=detail)

    return notifications
