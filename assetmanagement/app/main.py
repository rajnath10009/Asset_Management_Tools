from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlmodel import Session as SQLSession, create_engine, select
from .connect import Employee  
from datetime import datetime, timezone

app = FastAPI()

# Database connection 
DATABASE_URL = "mysql://root:544890raj@localhost/asset_management"
engine = create_engine(DATABASE_URL)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Employee creation schema (with password length validation)
class EmployeeCreate(BaseModel):
    employee_name: str
    email: str
    password: str = Field(..., min_length=6, max_length=20, description="Password must be between 6 and 20 characters")
    department: str
    designation: str

# Employee login schema
class EmployeeLogin(BaseModel):
    email: str
    password: str 

# Employee update schema
class EmployeeUpdate(BaseModel):
    employee_name: str
    email: str
    department: str
    designation: str

# Employee delete schema
class AdminDeleteRequest(BaseModel):
    admin_email: str

# Employee response schema
class EmployeeResponse(EmployeeCreate):
    employee_id: int
    date_joined: datetime

    class Config:
        from_attributes = True

# Helper function to get the database session
def get_db():
    with SQLSession(engine) as session:
        yield session

# Admin authentication function
def verify_admin(email: str, db: Session):
    db_employee = db.execute(select(Employee).where(Employee.email == email)).scalars().first()
    if not db_employee or not db_employee.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return db_employee

# Signup Route
@app.post("/signup")
def signup(employee: EmployeeCreate, db: Session = Depends(get_db)):
    # Admin privileges cannot be set by the user
    # Ensure `is_admin` is always set to False, even if provided
    # This prevents users from assigning themselves admin roles

    # Hash the password
    hashed_password = pwd_context.hash(employee.password)

    # Create a new employee object
    db_employee = Employee(
        employee_name=employee.employee_name,
        email=employee.email,
        password=hashed_password,
        department=employee.department,
        designation=employee.designation,
        date_joined=datetime.now(timezone.utc),
        is_admin=False  # Explicitly set to False, even if passed
    )

    # Save the employee to the database
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    # Return a success message
    return {
        "message": "Signup successful",
        "employee_id": db_employee.employee_id,
        "employee_name": db_employee.employee_name,
    }

# Login Route
@app.post("/login")
def login(login_data: EmployeeLogin, db: Session = Depends(get_db)):
    # Extract email and password from the request
    email = login_data.email
    password = login_data.password

    # Query the database for the user
    db_employee = db.execute(select(Employee).where(Employee.email == email)).scalars().first()

    # Check if the user exists
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )

    # Check if the password is correct
    if not pwd_context.verify(password, db_employee.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Return success response
    return {"message": "Login successful", "is_admin": db_employee.is_admin}

# Admin Route to Update Employee Details (no password and no is_admin changes)
@app.put("/admin/update-employee/{employee_id}")
def update_employee(
    employee_id: int,
    employee: EmployeeUpdate,  # Expect employee data to be passed in JSON body
    admin_email: str,  # admin_email is passed as a query parameter
    db: Session = Depends(get_db),
):
    # Verify if the requester is an admin
    verify_admin(admin_email, db)

    # Fetch the employee by ID
    db_employee = db.get(Employee, employee_id)
    if not db_employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    # Update the employee details 
    db_employee.employee_name = employee.employee_name
    db_employee.email = employee.email
    db_employee.department = employee.department
    db_employee.designation = employee.designation

    # Commit the changes to the database
    db.commit()
    db.refresh(db_employee)

    return {
        "message": "Employee details updated successfully",
        "employee_id": db_employee.employee_id,
        "employee_name": db_employee.employee_name,
    }

# Admin Route to Delete Employee
@app.delete("/admin/delete-employee/{employee_id}")
def delete_employee(
    employee_id: int,
    delete_request: AdminDeleteRequest,  # Expect admin_email in JSON body
    db: Session = Depends(get_db)
):
    # Verify if the requester is an admin
    verify_admin(delete_request.admin_email, db)

    # Fetch the employee
    db_employee = db.get(Employee, employee_id)
    if not db_employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    # Delete the employee
    db.delete(db_employee)
    db.commit()

    return {"message": "Employee deleted successfully"}
