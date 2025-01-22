from sqlmodel import SQLModel, create_engine, Session, TIMESTAMP
from typing import Optional
from datetime import datetime
from model import Asset

# Database connection string
DATABASE_URL = "mysql+mysqlconnector://root:446688@localhost/asset_management"

# Create database engine
engine = create_engine(DATABASE_URL)

# Function to insert data into the Asset table
def insert_asset(
    asset_type: str,
    asset_model: str,
    asset_sl_no: str,
    asset_purchasedate: datetime,
    asset_warranty_end: datetime,
    asset_status: str,
    allocated_to: int,
    assigned_date: Optional[datetime] = None,
    return_date: Optional[datetime] = None
):
    # Open a session with the database
    with Session(engine) as session:
        # Create a new Asset instance
        new_asset = Asset(
            asset_type=asset_type,
            asset_model=asset_model,
            asset_sl_no=asset_sl_no,
            asset_purchasedate=asset_purchasedate,
            asset_warranty_end=asset_warranty_end,
            asset_status=asset_status,
            allocated_to=allocated_to,
            assigned_date=assigned_date,
            return_date=return_date
        )
        # Add the new record to the session
        session.add(new_asset)
        # Commit the transaction
        session.commit()
        # Refresh to load the auto-generated ID
        session.refresh(new_asset)
        print(f"Asset inserted successfully with ID: {new_asset.asset_id}")


