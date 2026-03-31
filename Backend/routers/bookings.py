from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime
from typing import List
import models
import schemas
from database import get_db

router = APIRouter()

@router.get("/bookings", response_model=List[schemas.BookingResponse])
def get_bookings(account_id: int, db: Session = Depends(get_db)):
    # Ora models.Booking.parking esiste e non darà più errore 500!
    bookings = db.query(models.Booking).options(
        joinedload(models.Booking.parking),
        joinedload(models.Booking.plate)
    ).filter(models.Booking.account_id == account_id).all()
    return bookings

@router.post("/bookings", status_code=status.HTTP_201_CREATED, response_model=schemas.BookingResponse)
def create_booking(payload: dict, db: Session = Depends(get_db)):
    account_id = payload.get("account_id")
    booking_data = payload.get("booking")
    
    parking_id = booking_data["parking"]["parking_id"]
    plate_id = booking_data["plate"]["plate_id"]
    
    raw_date = booking_data.get("date")
    if raw_date:
        try:
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            parsed_date = date.today()
    else:
        parsed_date = date.today()
        
    new_booking = models.Booking(
        account_id=account_id,
        parking_id=parking_id,
        plate_id=plate_id,
        booking_name=booking_data.get("booking_name"),
        date=parsed_date, 
        days=booking_data.get("days"),
        slot_code=booking_data.get("slot_code")
    )
    db.add(new_booking)
    db.commit()
    
    # Query back with joinedload so Pydantic has the nested data to serialize
    full_booking = db.query(models.Booking).options(
        joinedload(models.Booking.parking),
        joinedload(models.Booking.plate)
    ).filter(models.Booking.booking_id == new_booking.booking_id).first()
    
    return full_booking

@router.patch("/bookings", response_model=schemas.BookingResponse)
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
    
    # Query back with joinedload
    full_booking = db.query(models.Booking).options(
        joinedload(models.Booking.parking),
        joinedload(models.Booking.plate)
    ).filter(models.Booking.booking_id == booking_id).first()
    
    return full_booking

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