from asset_insert_logic import insert_asset
from datetime import datetime

if __name__ == "__main__":
    insert_asset(
        asset_type="Laptop",
        asset_model="Dell Inspiron",
        asset_sl_no="D12345XYZ",
        asset_purchasedate=datetime(2023, 1, 10),
        asset_warranty_end=datetime(2025, 1, 10),
        asset_status="In Use",
        allocated_to=5,
        assigned_date=datetime(2023, 1, 10),
        return_date=None
    )
