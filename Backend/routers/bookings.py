from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime, timedelta
from typing import List
import models
import schemas
from database import get_db

router = APIRouter()


# --- Helpers ---

def _get_parking_or_404(db: Session, parking_id: int) -> models.Parking:
    parking = db.query(models.Parking).filter(
        models.Parking.parking_id == parking_id
    ).first()
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    return parking


def _count_overlapping_bookings(
    db: Session,
    parking_id: int,
    target_date: date,
    days: int,
    use_disabled: bool,
    exclude_booking_id: int | None = None,
) -> int:
    target_end = target_date + timedelta(days=days - 1)
    query = db.query(models.Booking).filter(
        models.Booking.parking_id == parking_id
    )
    if exclude_booking_id:
        query = query.filter(models.Booking.booking_id != exclude_booking_id)

    count = 0
    for b in query.all():
        b_end = b.date + timedelta(days=b.days - 1)
        if target_date <= b_end and target_end >= b.date:
            b_plate = db.query(models.Plate).filter(
                models.Plate.plate_id == b.plate_id
            ).first()
            b_user = db.query(models.User).filter(
                models.User.account_id == b_plate.account_id
            ).first() if b_plate else None
            b_disabled = b_user.is_disabled if b_user else False
            if b_disabled == use_disabled:
                count += 1
    return count


def _check_availability_for_date(
    db: Session,
    parking: models.Parking,
    target_date: date,
    days: int,
    use_disabled: bool,
    exclude_booking_id: int | None = None,
) -> None:
    occupied = _count_overlapping_bookings(
        db, parking.parking_id, target_date, days, use_disabled, exclude_booking_id
    )
    total = parking.disabled_slot if use_disabled else parking.total_slot
    tipo  = "disabled" if use_disabled else "regular"
    if total - occupied <= 0:
        raise HTTPException(
            status_code=403,
            detail=f"No {tipo} slots available from {target_date} for {days} day(s) "
                   f"({occupied}/{total} already booked)"
        )


def _check_slot_conflict(
    db: Session,
    parking_id: int,
    slot_code: int,
    booking_date: date,
    days: int,
    exclude_booking_id: int | None = None,) -> None:
    
    query = db.query(models.Booking).filter(
        models.Booking.parking_id == parking_id,
        models.Booking.slot_code  == slot_code,
    )
    if exclude_booking_id:
        query = query.filter(models.Booking.booking_id != exclude_booking_id)

    booking_end = booking_date + timedelta(days=days - 1)
    for b in query.all():
        b_end = b.date + timedelta(days=b.days - 1)
        if booking_date <= b_end and booking_end >= b.date:
            raise HTTPException(
                status_code=409,
                detail=f"Slot {slot_code} is already booked from {b.date} to {b_end}"
            )


def _parse_date(raw: str | None) -> date:
    if raw:
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            pass
    return date.today()


def _is_disabled_user(db: Session, plate_id: int) -> bool:
    plate = db.query(models.Plate).filter(models.Plate.plate_id == plate_id).first()
    if not plate:
        return False
    user = db.query(models.User).filter(
        models.User.account_id == plate.account_id
    ).first()
    return user.is_disabled if user else False



# --- Calls ---
@router.get("/bookings", response_model=List[schemas.BookingResponse])
def get_bookings(account_id: int, db: Session = Depends(get_db)):
    # Ora models.Booking.parking esiste e non darà più errore 500!
    bookings = db.query(models.Booking).options(
        joinedload(models.Booking.parking),
        joinedload(models.Booking.plate)
    ).filter(models.Booking.account_id == account_id).all()
    return bookings


@router.get("/bookings/availability")
def get_availability(
    parking_id: int,
    target_date: str,
    days: int = 1,
    db: Session = Depends(get_db)
):
    parking = _get_parking_or_404(db, parking_id)
    parsed  = _parse_date(target_date)

    booked_regular  = _count_overlapping_bookings(db, parking_id, parsed, days, use_disabled=False)
    booked_disabled = _count_overlapping_bookings(db, parking_id, parsed, days, use_disabled=True)

    return {
        "parking_id":         parking_id,
        "date":               str(parsed),
        "days":               days,
        "regular_total":      parking.total_slot,
        "regular_booked":     booked_regular,
        "regular_available":  parking.total_slot    - booked_regular,
        "disabled_total":     parking.disabled_slot,
        "disabled_booked":    booked_disabled,
        "disabled_available": parking.disabled_slot - booked_disabled,
    }


@router.post("/bookings", status_code=status.HTTP_201_CREATED, response_model=schemas.BookingResponse)
def create_booking(payload: dict, db: Session = Depends(get_db)):
    account_id   = payload.get("account_id")
    booking_data = payload.get("booking")
 
    parking_id = booking_data["parking"]["parking_id"]
    plate_id   = booking_data["plate"]["plate_id"]
    days       = booking_data.get("days", 1)
    slot_code  = booking_data.get("slot_code")
 
    parsed_date  = _parse_date(booking_data.get("date"))
    parking      = _get_parking_or_404(db, parking_id)
    use_disabled = _is_disabled_user(db, plate_id)
 
    # are there available slot for that date?
    _check_availability_for_date(db, parking, parsed_date, days, use_disabled)
 
    # is the slot free in that range
    if slot_code is not None:
        _check_slot_conflict(db, parking_id, slot_code, parsed_date, days)
 

    new_booking = models.Booking(
        account_id=account_id,
        parking_id=parking_id,
        plate_id=plate_id,
        booking_name=booking_data.get("booking_name"),
        date=parsed_date,
        days=days,
        slot_code=slot_code
    )
    db.add(new_booking)
    db.commit()
 
    return db.query(models.Booking).options(
        joinedload(models.Booking.parking),
        joinedload(models.Booking.plate)
    ).filter(models.Booking.booking_id == new_booking.booking_id).first()


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