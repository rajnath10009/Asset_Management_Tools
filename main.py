from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import List, Optional
from datetime import datetime
from model import Employee

# Create the database connection and engine
DATABASE_URL = "mysql://root:446688@localhost/asset_management"  # Replace with your MySQL credentials and DB name
engine = create_engine(DATABASE_URL)

# Create the FastAPI app
app = FastAPI()

# Define Pydantic models for request and response validation
class EmployeeCreate(BaseModel):
    employee_name: str
    email: str
    password: str
    department: str
    designation: str

class EmployeeResponse(EmployeeCreate):
    employee_id: int
    date_joined: datetime
    is_admin: bool = False

    class Config:
        from_attributes = True

# Dependency to get the database session
def get_db():
    with Session(engine) as session:
        yield session

# POST: Create a new employee
@app.post("/employees/", response_model=EmployeeResponse)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

# GET: Get all employees
@app.get("/employees/", response_model=List[EmployeeResponse])
def get_employees(db: Session = Depends(get_db)):
    employees = db.exec(select(Employee)).all()
    return employees

# GET: Get a specific employee by ID
@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    stmt = select(Employee).where(Employee.employee_id == employee_id)
    employee = db.exec(stmt).first()  # Execute the query and get the first result
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

