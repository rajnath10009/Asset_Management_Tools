from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
 
class Employee(SQLModel, table=True):  # Specify table=True for ORM mapping
    employee_id: Optional[int] = Field(default=None, primary_key=True)  # Removed autoincrement
    employee_name: str = Field(nullable=False, max_length=50)
    is_admin: bool = Field(default=False)
    email: str = Field(nullable=False, max_length=100, unique=True)
    password: str = Field(nullable=False, max_length=100)
    department: str = Field(nullable=False, max_length=50)
    designation: str = Field(nullable=False, max_length=50)
    date_joined: Optional[datetime] = Field(default_factory=datetime.now) 

# Define the AssetStatus enumeration
class AssetStatus(str, Enum):
    ALLOCATED = "allocated"
    MAINTENANCE = "maintenance"
    AVAILABLE = "available"

class AssetType(str, Enum):
    LAPTOP = "Laptop"
    MOUSE = "Mouse"
    MONITOR = "Monitor"
    SPEAKER="Speaker"
    KEYBOARD="Key-board"


class Asset(SQLModel, table=True):  # Specify table=True for ORM mapping
    asset_id: Optional[int] = Field(default=None, primary_key=True)  # Removed autoincrement
    asset_type: AssetType = Field(nullable=False),
    asset_model: str = Field(nullable=False, max_length=100)
    asset_sl_no: str = Field(nullable=False, max_length=8)
    asset_purchasedate: Optional[datetime] = Field(default_factory=datetime.now)
    asset_warranty_end: Optional[datetime] = Field(default_factory=datetime.now)
    asset_status: AssetStatus = Field(nullable=False)  # Enum for status
    allocated_to: int = Field(nullable=False, foreign_key="employee.employee_id")
 
class Notification(SQLModel, table=True):  # Specify table=True for ORM mapping
    notification_id: Optional[int] = Field(default=None, primary_key=True)  # Removed autoincrement
    sender_id: int = Field(nullable=False, foreign_key="employee.employee_id")
    recipient_id: int = Field(nullable=False, foreign_key="employee.employee_id")
    message: str = Field(nullable=False, unique=True, max_length=255)
    sent_at: Optional[datetime] = Field(default_factory=datetime.now)
    priority: int = Field(nullable=False) 
 
class Ticket(SQLModel, table=True):
    __tablename__ = 'Ticket'
    ticket_id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: Optional[int] = Field(default=None, foreign_key='employee.employee_id')
    asset_id: Optional[int] = Field(default=None, foreign_key='asset.asset_id')
    ticket_type: str = Field(nullable=False, max_length=50)
    ticket_status: Optional[int] = Field(default=None, foreign_key='notification.notification_id')
    assigned_date: Optional[datetime] = Field(default=datetime.today)
    return_date: Optional[datetime] = Field(default=datetime.today)
    returned_condition: str = Field(nullable=True, max_length=255)
    raised_at: Optional[datetime] = Field(default=datetime.now)
    resolved_at: Optional[datetime] = Field(default=datetime.now)
