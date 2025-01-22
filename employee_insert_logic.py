from sqlmodel import Session, create_engine
from model import Employee
from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime

# Database connection string
DATABASE_URL = "mysql+mysqlconnector://root:446688@localhost/asset_management"

# Create database engine
engine = create_engine(DATABASE_URL)

def insert_employee(
    employee_name: str,
    email: str,
    password: str,
    department: str,
    designation: str,
    date_joined: Optional[datetime] = None,
    is_admin: bool = False
):
    with Session(engine) as session:
        new_employee = Employee(
            employee_name=employee_name,
            email=email,
            password=password,
            department=department,
            designation=designation,
            date_joined=date_joined or datetime.now(),
            is_admin=is_admin
        )
        session.add(new_employee)
        session.commit()
        session.refresh(new_employee)
        print(f"Employee inserted successfully with ID: {new_employee.employee_id}")

