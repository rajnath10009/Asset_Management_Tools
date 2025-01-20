from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from test1 import Employee, engine # Import User model and engine from models.py
from datetime import datetime  
from pydantic import BaseModel
#from passlib.context import CryptContext  # Use this for hashing passwords
#import jwt  # We'll use JWT for generating tokens
#from datetime import datetime, timedelta

app = FastAPI()

# Dependency to get the database session
def get_db():
    with Session(engine) as db:  # Use SQLModel's Session to interact with the database
        yield db

class EmployeeLogin(BaseModel):
    email: str
    password: str

# Endpoint to get a user by ID
@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        statement = select(Employee).where(Employee.employee_id == user_id)
        db_user = db.exec(statement).first()  # .first() instead of .scalars().first() for simplicity
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Endpoint to create a new user
@app.post("/users/")
def create_user(employee_name: str,email: str,password: str, department: str,designation: str, db: Session = Depends(get_db)):
    # Create a new user and insert it into the database
    db_user = Employee(employee_name=employee_name, email=email, password=password,department=department,designation=designation)
    db.add(db_user)
    db.commit()  # Commit the transaction to insert the user
    db.refresh(db_user)  # Refresh to get the new ID and other values
    return db_user


# Endpoint to handle login
@app.post("/login/")
def login_employee(employee: EmployeeLogin, db: Session = Depends(get_db)):
    # Check if the email exists
    db_user = db.exec(select(Employee).where(Employee.email == employee.email)).first()

    if db_user is None:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Check if the password is correct
    if db_user.password != employee.password:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # If the credentials are correct, return the user info or a success message
    return {"message": "Login successful", "user": db_user}
















'''
# Initialize CryptContext for password hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key for JWT encoding (make sure to keep this secret and secure)
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time

# Dependency to get the database session
def get_db():
    with Session(engine) as db:
        yield db



# Function to verify password using bcrypt
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/login")
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    # Query the employee by username
    statement = select(Employee).where(Employee.employee_id == login_request.username)
    db_employee = db.exec(statement).first()

    # If employee doesn't exist, raise 404
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Verify password (in production, use hashed passwords, not plain text)
    if not verify_password(login_request.password, db_employee.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Create JWT token with employee data (e.g., username or employee_id)
    access_token = create_access_token(data={"sub": db_employee.username})
    
    # Return the token to the user
    return {"access_token": access_token, "token_type": "bearer"}

'''






'''# Endpoint to update an existing user
@app.put("/users/{user_id}")
def update_user(user_id: int, name: str, email: str, db: Session = Depends(get_db)):
    # Fetch the user from the database
    db_user = db.execute(select(Employee).where(Employee.employee_id == user_id)).scalars().first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update the user information
    db_user.name = name
    db_user.email = email
    db.commit()  # Commit the changes to the database
    db.refresh(db_user)  # Refresh the object to get the latest data
    return db_user

# Endpoint to delete a user
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Fetch the user to be deleted
    db_user = db.execute(select(Employee).where(Employee.employee_id == user_id)).scalars().first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete the user
    #db.delete(db_user)
    #db.commit()  # Commit the transaction
    #return {"message": "User deleted successfully"}'''
