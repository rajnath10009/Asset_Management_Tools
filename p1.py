from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlmodel import Session as SQLSession, create_engine, select
from model import Employee,Asset
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

# Admin delete schema
class AdminDeleteRequest(BaseModel):
    admin_email: str
    
# Asset creation schema
class AssetCreate(BaseModel):
    asset_type: str
    asset_model: str
    asset_sl_no: int
    asset_purchasedate: datetime
    asset_status: str
    allocated_to: int
    
# Database session dependency
def get_db():
    with SQLSession(engine) as session:
        yield session

# Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# JWT token creation function
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Admin authentication function using JWT
def verify_admin(token: str, db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        db_employee = db.execute(select(Employee).where(Employee.email == email)).scalars().first()
        if not db_employee or not db_employee.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except jwt.PyJWTError:
        raise credentials_exception
from fastapi import Query

@app.post("/login")
def login(
    email: str = Query(..., description="Employee email"),
    password: str = Query(..., description="Employee password"),
    db: Session = Depends(get_db)
):
    # Query the database for the user
    db_employee = db.execute(select(Employee).where(Employee.email == email)).scalars().first()

    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )

    # Check if the password is correct
    if not verify_password(password, db_employee.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create and return JWT token
    access_token = create_access_token(data={"sub": db_employee.email})
    return {"access_token": access_token, "token_type": "bearer"}
@app.post("/admin/add-employee")
def add_employee(
    employee_name: str = Query(..., description="Employee Name"),
    email: str = Query(..., description="Employee Email"),
    password: str = Query(..., description="Employee Password"),
    department: str = Query(..., description="Employee Department"),
    designation: str = Query(..., description="Employee Designation"),
    token: str = Query(..., description="Admin JWT token"),
    db: Session = Depends(get_db)
):
    # Verify if the requester is an admin
    verify_admin(token, db)

    # Hash the employee's password
    hashed_password = pwd_context.hash(password)

    # Create a new employee object
    db_employee = Employee(
        employee_name=employee_name,
        email=email,
        password=hashed_password,
        department=department,
        designation=designation,
        date_joined=datetime.now(timezone.utc),
        is_admin=False  # Default to non-admin employees
    )

    # Check if the email already exists
    existing_employee = db.execute(select(Employee).where(Employee.email == email)).scalars().first()
    if existing_employee:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    # Save the employee to the database
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    return {
        "message": "Employee added successfully",
        "employee_id": db_employee.employee_id,
        "employee_name": db_employee.employee_name,
    }

@app.put("/admin/update-employee/{employee_id}")
def update_employee(
    employee_id: int,
    employee_name: str = Query(..., description="Updated Employee Name"),
    email: str = Query(..., description="Updated Employee Email"),
    department: str = Query(..., description="Updated Employee Department"),
    designation: str = Query(..., description="Updated Employee Designation"),
    token: str = Query(..., description="Admin JWT token"),
    db: Session = Depends(get_db),
):
    # Verify if the requester is an admin
    verify_admin(token, db)

    # Fetch the employee by ID
    db_employee = db.get(Employee, employee_id)
    if not db_employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    # Update the employee details
    db_employee.employee_name = employee_name
    db_employee.email = email
    db_employee.department = department
    db_employee.designation = designation

    db.commit()
    db.refresh(db_employee)

    return {
        "message": "Employee details updated successfully",
        "employee_id": db_employee.employee_id,
        "employee_name": db_employee.employee_name,
    }



@app.delete("/admin/delete-employee/{employee_id}")
def delete_employee(
    employee_id: int,
    token: str = Query(..., description="Admin JWT token"),
    db: Session = Depends(get_db)
):
    # Verify if the requester is an admin
    verify_admin(token, db)

    # Fetch the employee
    db_employee = db.get(Employee, employee_id)
    if not db_employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    # Delete the employee
    db.delete(db_employee)
    db.commit()

    return {"message": "Employee deleted successfully"}

## asset
# Admin Route to Add Asset
@app.post("/admin/assets/add")
async def add_asset(
    asset: AssetCreate, 
    token: str, 
    db: Session = Depends(get_db)
):
    # Verify if the requester is an admin
    verify_admin(token, db)

    # Calculate warranty expiration date
    warranty = asset.asset_purchasedate.replace(year=asset.asset_purchasedate.year + 2)
    asset_types = ["laptop", "mouse", "monitor", "keyboard", "speaker"]

    # Validate asset type
    if asset.asset_type not in asset_types:
        raise HTTPException(status_code=404, detail="Invalid asset type")

    # Create a new asset record
    db_asset = Asset(
        asset_type=asset.asset_type,
        asset_model=asset.asset_model,
        asset_sl_no=asset.asset_sl_no,
        asset_purchasedate=asset.asset_purchasedate,
        asset_warranty_end=warranty,
        asset_status=asset.asset_status,
        allocated_to=asset.allocated_to,
    )

    try:
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

    return {"message": "Asset added successfully", "asset_id": db_asset.asset_id}

# Admin Route to List All Assets
@app.get("/admin/assets/list", response_model=List[Asset])
async def get_all_assets(
    token: str, 
    db: Session = Depends(get_db)
):
    # Verify if the requester is an admin
    verify_admin(token, db)

    # Retrieve all assets
    assets = db.execute(select(Asset)).scalars().all()
    return assets

# Admin Route to Update Asset
@app.put("/admin/assets/update/{asset_id}")
async def update_asset(
    asset_id: int, 
    asset: AssetCreate, 
    token: str, 
    db: Session = Depends(get_db)
):
    # Verify if the requester is an admin
    verify_admin(token, db)

    # Fetch the asset by ID
    db_asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Update asset details
    db_asset.asset_type = asset.asset_type
    db_asset.asset_model = asset.asset_model
    db_asset.asset_sl_no = asset.asset_sl_no
    db_asset.asset_purchasedate = asset.asset_purchasedate
    db_asset.asset_status = asset.asset_status
    db_asset.allocated_to = asset.allocated_to

    # Update warranty if purchase date changes
    if asset.asset_purchasedate:
        db_asset.asset_warranty_end = asset.asset_purchasedate.replace(year=asset.asset_purchasedate.year + 2)

    db.commit()
    db.refresh(db_asset)

    return {"message": "Asset updated successfully", "asset": db_asset}

# Admin Route to Delete Asset
@app.delete("/admin/assets/delete/{asset_id}")
async def delete_asset(
    asset_id: int, 
    token: str, 
    db: Session = Depends(get_db)
):
    # Verify if the requester is an admin
    verify_admin(token, db)

    # Fetch the asset by ID
    db_asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Delete the asset
    db.delete(db_asset)
    db.commit()

    return {"message": "Asset deleted successfully"}