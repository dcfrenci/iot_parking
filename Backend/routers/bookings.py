from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime
import models
from database import get_db

router = APIRouter()

@router.get("/bookings")
def get_bookings(account_id: int, db: Session = Depends(get_db)):
    bookings = db.query(models.Booking).filter(models.Booking.account_id == account_id).all()
    return bookings

@router.post("/bookings", status_code=status.HTTP_201_CREATED)
def create_booking(payload: dict, db: Session = Depends(get_db)):
    account_id = payload.get("account_id")
    booking_data = payload.get("booking")
    
    # Extract IDs from nested objects per yaml schema
    parking_id = booking_data["parking"]["parking_id"]
    plate_id = booking_data["plate"]["plate_id"]
    
    # --- 2. Safely handle the date field ---
    raw_date = booking_data.get("date")
    if raw_date:
        try:
            # Parse the string if it's a valid date (e.g., "2024-05-20")
            # If it comes with time like ISO 8601, you might need fromisoformat()
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            # Fallback if the format is weird
            parsed_date = date.today()
    else:
        # Fallback if the date is an empty string "" or None
        parsed_date = date.today()
        
    new_booking = models.Booking(
        account_id=account_id,
        parking_id=parking_id,
        plate_id=plate_id,
        booking_name=booking_data.get("booking_name"),
        date=parsed_date, # <-- 3. Pass the parsed Python date object
        days=booking_data.get("days"),
        slot_code=booking_data.get("slot_code")
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking
@router.patch("/bookings")
def update_booking(payload: dict, db: Session = Depends(get_db)):
    account_id = payload.get("account_id")
    booking_data = payload.get("booking")
    booking_id = booking_data.get("booking_id")
    
    booking = db.query(models.Booking).filter(
        models.Booking.booking_id == booking_id,
        models.Booking.account_id == account_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    booking.booking_name = booking_data.get("booking_name", booking.booking_name)
    booking.days = booking_data.get("days", booking.days)
    booking.date = booking_data.get("date", booking.date)
    booking.slot_code = booking_data.get("slot_code", booking.slot_code)
    
    db.commit()
    db.refresh(booking)
    return booking

@router.delete("/bookings")
def delete_booking(account_id: int, booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(
        models.Booking.booking_id == booking_id,
        models.Booking.account_id == account_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    db.delete(booking)
    db.commit()
    return {"detail": "Booking deleted"}