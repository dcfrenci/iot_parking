from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Booking, Parking, Plate
from schemas import BookingCreate, BookingResponse, UpdateBookingPlateDto
from datetime import datetime

router = APIRouter(prefix="/v1")


def _next_slot_code(db: Session) -> str:
    """Genera il prossimo slot code disponibile."""
    count = db.query(Booking).count()
    letter = chr(ord("A") + count // 10)
    number = count % 10 + 1
    return f"{letter}{number:02d}"


@router.get("/bookings", response_model=list[BookingResponse])
def get_bookings(user_id: int, db: Session = Depends(get_db)):
    return db.query(Booking).filter(Booking.user_id == user_id).all()


@router.post("/bookings", response_model=BookingResponse, status_code=201)
def create_booking(body: BookingCreate, user_id: int, db: Session = Depends(get_db)):
    parking = db.query(Parking).filter(Parking.id == body.parking_id).first()
    if parking is None:
        raise HTTPException(status_code=404, detail="Parking not found")

    db_booking = Booking(
        name       = body.name,
        parking_id = body.parking_id,
        car_plate  = body.car_plate,
        days       = body.days,
        date       = datetime.now(),
        slot_code  = _next_slot_code(db),
        user_id    = user_id,
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


@router.patch("/bookings/{booking_id}", response_model=BookingResponse)
def update_booking_plate(booking_id: int, body: UpdateBookingPlateDto, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    plate_exists = db.query(Plate).filter(Plate.plate_text == body.car_plate).first()
    if plate_exists is None:
        raise HTTPException(status_code=400, detail="Plate not registered")

    booking.car_plate = body.car_plate
    db.commit()
    db.refresh(booking)
    return booking
