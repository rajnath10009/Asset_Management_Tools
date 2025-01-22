
from fastapi import FastAPI, HTTPException, Depends, status, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlmodel import Session as SQLSession, create_engine, SQLModel, select
from connect import Employee
from connect import Asset
from typing import List, Optional
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
  # Assuming this is where the SQLAlchemy models are defined
from datetime import datetime, timedelta
from typing import Optional
import os

# Secret key for signing the JWT
# SECRET_KEY = "Arpita"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
# def create_jwt_token(user_id: int):
#     payload = {
#         "user_id": user_id,
#         "exp": datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
#     }
#     token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
#     return token
# Database connection string
DATABASE_URL = "mysql://root:54321@localhost/asset_management"
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

# Asset creation schema
class AssetCreate(BaseModel):
    asset_type: str
    asset_model: str
    asset_sl_no: int
    asset_purchasedate: datetime
    asset_status: str
    allocated_to: int

# Helper function to get the database session
def get_db():
    with SQLSession(engine) as session:
        yield session

# def create_jwt_token(user_id: int):
#     payload = {
#         "user_id": user_id,
#         "exp": datetime.utcnow() + timedelta(hours=1)
#     }
#     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#     return token

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: int = payload.get("user_id")
#         if user_id is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#     user = db.query(Employee).filter(Employee.employee_id == user_id).first()
#     if user is None:
#         raise credentials_exception
#     return user


# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)




# # Signup Route
# @app.post("/signup")
# async def signup(employee: EmployeeCreate, db: Session = Depends(get_db)):
#     # Hash the password
#     hashed_password = pwd_context.hash(employee.password)
 
#     # Create a new employee object
#     db_employee = Employee(
#         employee_name=employee.employee_name,
#         email=employee.email,
#         password=hashed_password,
#         department=employee.department,
#         designation=employee.designation,
#         date_joined=datetime.utcnow(),
#         is_admin=False,
#     )
 
    # # Save the employee to the database
    # db.add(db_employee)
    # db.commit()
    # db.refresh(db_employee)
 
    # Return a success message
    # return {
    #     "message": "Signup successful",
    #     "employee_id": db_employee.employee_id,
    #     "employee_name": db_employee.employee_name
    # }
# # Login Route
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

# AddAsset Route
@app.post("/admin/assets/add")
async def addAsset(asset: AssetCreate, db: Session = Depends(get_db)):
    warranty = asset.asset_purchasedate.replace(year=asset.asset_purchasedate.year + 2)
    # Create a new asset object
    Asset_list=["laptop","mouse","monitor","key-board","speaker"]
    if asset.asset_type not in Asset_list:
        raise HTTPException(status_code=404, detail="Asset type not available")
    db_asset = Asset(
        asset_type= asset.asset_type,
        asset_model= asset.asset_model,
        asset_sl_no= asset.asset_sl_no,
        asset_purchasedate= asset.asset_purchasedate,
        asset_warranty_end= warranty,
        asset_status= asset.asset_status,
        allocated_to=asset.allocated_to,
    )
    # Save the employee to the database
    try:
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
    except Exception as e:
        db.rollback()  # Roll back the transaction in case of an error
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
 
    # Return a success message
    return {
        "message": "Asset added successfully",
    }
 # API to print all asset details(ADMIN)
@app.get("/assets/list", response_model=List[Asset])
async def get_all_assets(db: Session = Depends(get_db)):
    assets = db.exec(select(Asset)).all()
    return assets

@app.put("/assets/update/{asset_id}")
async def update_asset(asset_id: int, asset: AssetCreate, db: Session = Depends(get_db)):
    # Fetch the existing asset by ID
    db_asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
# Check if asset exists
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Update the asset's details
    db_asset.asset_type = asset.asset_type
    db_asset.asset_model = asset.asset_model
    db_asset.asset_sl_no = asset.asset_sl_no
    db_asset.asset_purchasedate = asset.asset_purchasedate
    db_asset.asset_status = asset.asset_status
    db_asset.allocated_to = asset.allocated_to

    # Recalculate warranty if the purchased date is updated
    if asset.asset_purchasedate:
        db_asset.asset_warranty_end = asset.asset_purchasedate.replace(year=asset.asset_purchasedate.year + 2)

    # Commit the changes to the database
    db.commit()
    db.refresh(db_asset)

    # Return a success message with the updated asset data
    return {
        "message": "Asset updated successfully",
        "asset": db_asset
    }

# @app.delete("/assets/delete/{asset_id}")
# async def delete_asset(asset_id: int, db: Session = Depends(get_db)):
#     # Fetch the asset by ID
#     db_asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()

#     # Check if asset exists
#     if not db_asset:
#         raise HTTPException(status_code=404, detail="Asset not found")
    
#     # Delete the asset from the database
#     db.delete(db_asset)
#     db.commit()

#     # Return a success message
#     return {
#         "message": "Asset deleted successfully"
#     }

# #user
# @app.get("/assets/list", response_model=List[Asset])  
# async def get_all_assets(user_id: int, db: Session = Depends(get_db)):
#     # Get the user from the database
#     user = db.exec(select(Employee).where(Employee.employee_id == user_id)).first()
    
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     if user.is_admin:
#         # If the user is an sadmin, return all assets
#         assets = db.exec(select(Asset)).all()
#     else:
#         # If the user is not an admin, return only assets allocated to them
#         assets = db.exec(select(Asset).where(Asset.allocated_to == user_id)).all()
    
#     return assets


# @app.delete("/assets/delete/{asset_id}")
# async def delete_asset(
#     asset_id: int, 
#     #current_user: Employee = Depends(get_current_user), 
#     db: Session = Depends(get_db)
# ):
#     # Check if the current user is an admin
#     # if current_user.is_admin:
#     #     raise HTTPException(status_code=403, detail="Not authorized to delete assets")

#     # Fetch the asset by ID
#     db_asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()

#     # Check if asset exists
#     if not db_asset:
#         raise HTTPException(status_code=404, detail="Asset not found")
    
#     # Delete the asset from the database
#     db.delete(db_asset)
#     db.commit()

#     # Return a success message
#     return {
#         "message": "Asset deleted successfully"
#     }
@app.delete("/assets/delete/{asset_id}")
async def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    # Fetch the asset by ID
    db_asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()

    # Check if asset exists
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Delete the asset from the database
    db.delete(db_asset)
    db.commit()

    # Return a success message
    return {
        "message": "Asset deleted successfully"
    }

# @app.get("/user_id")
# async def get_user_id(current_user: Employee = Depends(get_current_user)):
#     return {"user_id": current_user.employee_id}