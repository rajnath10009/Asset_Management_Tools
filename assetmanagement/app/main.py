# from fastapi import FastAPI, HTTPException, Depends, status, Request, Form
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from passlib.context import CryptContext
# from sqlmodel import Session as SQLSession, create_engine, SQLModel, select
# from .connect import Employee  # Assuming this is where the SQLAlchemy models are defined
# from datetime import datetime

# import os

# app = FastAPI()

# # Database connection string
# DATABASE_URL = "mysql://root:544890raj@localhost/asset_management"
# engine = create_engine(DATABASE_URL)

# # Password hashing context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Configure the templates directory path
# templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), 'templates'))

# class EmployeeCreate(BaseModel):
#     employee_name: str
#     email: str
#     password: str
#     department: str
#     designation: str

# class EmployeeResponse(EmployeeCreate):
#     employee_id: int
#     date_joined: datetime
#     is_admin: bool = False
 
#     class Config:
#         from_attributes = True

# # Helper function to get the database session
# def get_db():
#     with SQLSession(engine) as session:
#         yield session

# # Signup Route
# @app.post("/signup", response_model=EmployeeResponse)
# async def signup(employee: EmployeeCreate, db: Session = Depends(get_db)):
#     hashed_password = pwd_context.hash(employee.password)
#     db_employee = Employee(
#         employee_name=employee.employee_name,
#         email=employee.email,
#         password=hashed_password,
#         department=employee.department,
#         designation=employee.designation
#     )
#     db.add(db_employee)
#     db.commit()
#     db.refresh(db_employee)
#     return {"message": "User created successfully"}

# # Login Route (Fixed)
# @app.post("/login")
# async def login(
#     email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
# ):
#     db_employee = db.execute(select(Employee).where(Employee.email == email)).scalars().first()
#     if db_employee is None or not pwd_context.verify(password, db_employee.password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
#     return {"message": "Login successful"}

# # Root to serve the HTML page
# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

from fastapi import FastAPI, HTTPException, Depends, status, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlmodel import Session as SQLSession, create_engine, SQLModel, select
from .connect import Employee  # Assuming this is where the SQLAlchemy models are defined
from datetime import datetime
from typing import Optional

import os

app = FastAPI()

# Database connection string
DATABASE_URL = "mysql://root:544890raj@localhost/asset_management"
engine = create_engine(DATABASE_URL)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure the templates directory path
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), 'templates'))


# Employee creation schema
class EmployeeCreate(BaseModel):
    employee_name: str
    email: str
    password: str
    department: str
    designation: str


# Employee response schema
class EmployeeResponse(EmployeeCreate):
    employee_id: int
    date_joined: datetime
    is_admin: Optional[bool] = False

    class Config:
        from_attributes = True


# Helper function to get the database session
def get_db():
    with SQLSession(engine) as session:
        yield session


# Signup Route
@app.post("/signup", response_model=EmployeeResponse)
async def signup(employee: EmployeeCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(employee.password)
    db_employee = Employee(
        employee_name=employee.employee_name,
        email=employee.email,
        password=hashed_password,
        department=employee.department,
        designation=employee.designation,
        date_joined=datetime.utcnow(),
        is_admin=False
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


# Login Route
@app.post("/login")
async def login(
    email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    db_employee = db.execute(select(Employee).where(Employee.email == email)).scalars().first()
    if db_employee is None or not pwd_context.verify(password, db_employee.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"message": "Login successful"}


# Root to serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
