# from fastapi import FastAPI, HTTPException, Depends
# from sqlmodel import SQLModel, Field, Session, create_engine, select
# from typing import Optional
# from datetime import datetime
# from pydantic import BaseModel
# from model import Employee

# # Database URL - Use an appropriate database URL
# DATABASE_URL = "mysql://root:446688@localhost/asset_management"

# # Create the engine and session
# engine = create_engine(DATABASE_URL, echo=True)

# # Initialize the FastAPI app
# app = FastAPI()

# # Dependency to get the database session
# def get_session():
#     with Session(engine) as session:
#         yield session

# # Create the database tables
# SQLModel.metadata.create_all(bind=engine)

# # Pydantic schema for request and response validation
# class EmployeeCreate(BaseModel):
#     employee_name: str
#     is_admin: Optional[bool] = False
#     email: str
#     password: str
#     department: str
#     designation: str

# class EmployeeResponse(EmployeeCreate):
#     employee_id: int
#     date_joined: datetime

#     class Config:
#         from_attributes = True

# # GET endpoint to fetch all employees
# @app.get("/employees/", response_model=list[EmployeeResponse])
# async def get_employees(session: Session = Depends(get_session)):
#     employees = session.exec(select(Employee)).all()
#     return employees

# # POST endpoint to create a new employee
# @app.post("/employees/", response_model=EmployeeResponse)
# async def create_employee(employee: EmployeeCreate, session: Session = Depends(get_session)):
#     db_employee = Employee(**employee.dict())
#     session.add(db_employee)
#     session.commit()
#     session.refresh(db_employee)
#     return db_employee

from fastapi import FastAPI, HTTPException, Depends, status, Header
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from jose import JWTError, jwt

# Database URL
DATABASE_URL = "mysql://root:446688@localhost/asset_management"
# Create the engine and session
engine = create_engine(DATABASE_URL, echo=True)

# Initialize the FastAPI app
app = FastAPI()

# Secret key for JWT encoding/decoding
SECRET_KEY = "6e7abf2d8e88811889d50e9f5e3c15858ac6245b2797c8f722f47b22c3ab075a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # Expiry time for the access token in minutes
 # Expiry time for the access token

# Dependency to get the database session
def get_session():
    with Session(engine) as session:
        yield session

# Employee model
class Employee(SQLModel, table=True):
    employee_id: Optional[int] = Field(default=None, primary_key=True)
    employee_name: str = Field(nullable=False, max_length=50)
    is_admin: bool = Field(default=False)
    email: str = Field(nullable=False, max_length=100, unique=True)
    password: str = Field(nullable=False, max_length=100)
    department: str = Field(nullable=False, max_length=50)
    designation: str = Field(nullable=False, max_length=50)
    date_joined: Optional[datetime] = Field(default_factory=datetime.now)

# Pydantic schema for request and response validation
class EmployeeCreate(BaseModel):
    employee_name: str
    is_admin: Optional[bool] = False
    email: str
    password: str
    department: str
    designation: str

class EmployeeResponse(EmployeeCreate):
    employee_id: int
    date_joined: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str
    is_admin: bool

# Create the database tables
SQLModel.metadata.create_all(bind=engine)

# Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to verify JWT token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=403, detail="Token is invalid")
        return TokenData(email=email, is_admin=payload.get("is_admin", False))
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid")

# Get employee by email (used in login)
def get_employee_by_email(session: Session, email: str):
    return session.query(Employee).filter(Employee.email == email).first()

# POST endpoint to create new employee
@app.post("/employees", response_model=EmployeeResponse)
async def create_employee(employee: EmployeeCreate, session: Session = Depends(get_session)):
    db_employee = Employee(**employee.dict())
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee

# POST endpoint to login and return JWT token (Custom Bearer Token)
@app.post("/login", response_model=Token)
async def login_for_access_token(email: str, password: str, session: Session = Depends(get_session)):
    user = get_employee_by_email(session, email)
    if user is None or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user.email, "is_admin": user.is_admin}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protect routes that require authentication using JWT Bearer Token
# @app.get("/get", response_model=list[EmployeeResponse])
# async def get_employees(authorization: str = Header(...), session: Session = Depends(get_session)):
#     token = authorization.split(" ")[1]  # Extract token from Bearer <token>
#     user = verify_token(token)  # Check if the token is valid
#     employees = session.exec(select(Employee)).all()
#     return employees
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        if not email:
            raise HTTPException(status_code=403, detail="Token is invalid")
        return {"email": email, "is_admin": is_admin}
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid")

@app.get("/get", response_model=List[EmployeeResponse])
async def get_employees(authorization: str = Header(...), session: Session = Depends(get_session)):
    print(f"Authorization header: {authorization}")  # Log authorization header

    # Check if the Authorization header is in the correct format
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid authorization header format")
    
    # Extract token from Bearer <token>
    token = authorization.split(" ")[1]
    print(f"Extracted token: {token}")  # Log extracted token

    # Verify token and log the returned user
    user = verify_token(token)
    print(f"Decoded token user: {user}")  # Log decoded user

    # Check if the user is an admin
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource")

    # Fetch employees from the database
    employees = session.exec(select(Employee)).all()
    print(f"Fetched employees: {employees}")  # Log fetched employees
    return employees
