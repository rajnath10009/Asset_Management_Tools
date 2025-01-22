from sqlmodel import SQLModel, create_engine, Session
from datetime import datetime
from model import Notification
from asset_insert_logic import DATABASE_URL, engine
from typing import Optional


# Function to insert data into the Notification table
def insert_notification(
    sender_id: int,
    recipient_id: int,
    message: str,
    priority: int,
    sent_at: Optional[datetime] = None
):
    # Open a session with the database
    with Session(engine) as session:
        # Create a new Notification instance
        new_notification = Notification(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message=message,
            priority=priority,
            sent_at=sent_at or datetime.now()  # Use current time if none is provided
        )
        # Add the new record to the session
        session.add(new_notification)
        # Commit the transaction
        session.commit()
        # Refresh to load the auto-generated ID
        session.refresh(new_notification)
        print(f"Notification inserted successfully with ID: {new_notification.notification_id}")

# Ensure this block is outside the function
if __name__ == "__main__":
    insert_notification(
        sender_id=1,
        recipient_id=2,
        message="Your request has been approved.",
        priority=1
    )
