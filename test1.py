from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, func, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Define the database connection string
DATABASE_URL = "mysql+pymysql://root:qwerty111@localhost/proj"
 
# Replace <username>, <password>, <host>, and <database_name> with your details
# Example: "mysql+pymysql://root:password@localhost/UserManagement"
 
# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a declarative base
Base = declarative_base()
 
# Define a User table
class Employee(Base):
    __tablename__ = 'Employee'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    is_admin = Column(Boolean, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=False)
    ph_no = Column(Integer, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

class Notification(Base):
    __tablename__ = 'Notification'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient_id =Column(Integer, ForeignKey('Employee.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('Employee.id'), nullable=False)
    message = Column(String(100))
    sent_at = Column(TIMESTAMP , nullable=False)
    priority =Column(Integer, nullable=False)
    

class Asset(Base):
    __tablename__ = 'Asset'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    sl_no = Column(Integer, nullable=False)
    purchase_date = Column(TIMESTAMP, default = func.now())
    warranty_end = Column(TIMESTAMP , default = func.now())
    status = Column(String(20), nullable=False)
    allocated_to = Column(Integer, ForeignKey('Employee.id'))



class Ticket(Base):
    __tablename__ = 'Ticket'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id =Column(Integer, ForeignKey('Employee.id'), nullable=False)
    asset_id = Column(Integer, nullable=False)
    ticket_type = Column(String(100), nullable=False)
    ticket_status = Column(String(100), nullable=False)
    assigned_date = Column(TIMESTAMP , default = func.now)
    returned_date = Column(TIMESTAMP, nullable=False)
    returned_condition = Column(String(100), nullable=False)
    raised_at = Column(TIMESTAMP , nullable=False)
    resolved_at = Column(TIMESTAMP , nullable=False)


 
# Create the tables in the database
# Base.metadata.create_all(engine)
 
# Create a session to interact with the database
# Session = sessionmaker(bind=engine)
# session = Session()
 
'''# Add a sample user
new_user = User(name="Alice", email="alice@example.com", password="securepassword")
session.add(new_user)
session.commit()
 
# Query the users
users = session.query(User).all()
for user in users:
    print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")'''