from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import models, schemas
from database import get_db
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
from mqtt_client import mqtt_manager

load_dotenv()

router = APIRouter()

PARKING_ID = int(os.getenv("PARKING_ID", 1))

# AGGIUNGERE intero blocco prima di @router.post("/gate/entry")

def _decrement_slot(parking: models.Parking, use_disabled: bool) -> bool:
    if use_disabled and parking.available_disabled_slot > 0:
        parking.available_disabled_slot -= 1
        return True
    elif parking.available_slot > 0:
        parking.available_slot -= 1
        return False
    else:
        raise HTTPException(
            status_code=403,
            detail="No available slots"
        )


def _increment_slot(parking: models.Parking, used_disabled: bool) -> None:
    if used_disabled:
        parking.available_disabled_slot = min(
            parking.disabled_slot,
            parking.available_disabled_slot + 1
        )
    else:
        parking.available_slot = min(
            parking.total_slot,
            parking.available_slot + 1
        )


@router.post("/gate/entry")
def gate_entry(data: schemas.GateEntryRequest, db: Session = Depends(get_db)):

    # Plate verify
    plate = db.query(models.Plate).filter(models.Plate.plate_text == data.plate_text).first()
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not registered")
    if not plate.is_active:
        raise HTTPException(status_code=403, detail="Plate is not active")

    # Verify if session already active
    existing = db.query(models.Parked).filter(
        models.Parked.plate_id == plate.plate_id,
        models.Parked.is_paid == False
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle already has an active session")
    
    # Verify user disabled status
    user = db.query(models.User).filter(
        models.User.account_id == plate.account_id
    ).first()
    use_disabled = user.is_disabled if user else False

    parking = db.query(models.Parking).filter(models.Parking.parking_id == PARKING_ID).first()
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    
    assigned_disabled = _decrement_slot(parking, use_disabled)

    new_session = models.Parked(
        plate_id=plate.plate_id,
        parking_id=PARKING_ID,
        entry_time=datetime.now(),
        amount=0.0,
        is_paid=False,
        used_disabled_slot=assigned_disabled
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # TODO: uncomment when real data collection is needed
    # new_record = models.ParkinHistory(
    #     parking_id=PARKING_ID,
    #     timestamp=datetime.now(),
    #     occupied_slots=parking.total_slot - parking.available_slot,
    #     disabled_occupied_slots=parking.disabled_slot - parking.available_disabled_slot
    # )
    # db.add(new_record)
    # db.commit()

    mqtt_manager.publish("parking/gate/entry", "o1")

    return {"status": "ok", "plate": data.plate_text}


@router.post("/gate/exit")
def gate_exit(data: schemas.GateExitRequest, db: Session = Depends(get_db)):

    plate = db.query(models.Plate).filter(models.Plate.plate_text == data.plate_text).first()
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not registered")
    if not plate.is_active:
        raise HTTPException(status_code=403, detail="Plate is not active")

    session = db.query(models.Parked).filter(
        models.Parked.plate_id == plate.plate_id,
        models.Parked.is_paid == False
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")

    # FIX 1: Anti-Race Condition check (Prevent immediate exit from double-read)
    duration_seconds = (datetime.now() - session.entry_time).total_seconds()
    if duration_seconds < 60: # Must be inside for at least 60 seconds
        raise HTTPException(status_code=400, detail="Session too short to exit (double read prevented)")

    parking = db.query(models.Parking).filter(models.Parking.parking_id == PARKING_ID).first()
    
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    duration_hours = duration_seconds / 3600
    session.amount = round(duration_hours * parking.price_per_hour, 2)
    session.is_paid = True

    _increment_slot(parking, session.used_disabled_slot)

    db.commit()

    # TODO: uncomment when real data collection is needed
    # new_record = models.ParkinHistory(
    #     parking_id=PARKING_ID,
    #     timestamp=datetime.now(),
    #     occupied_slots=parking.total_slot - parking.available_slot,
    #     disabled_occupied_slots=parking.disabled_slot - parking.available_disabled_slot
    # )
    # db.add(new_record)
    # db.commit()

    mqtt_manager.publish("parking/gate/exit", "o2")

    return {"status": "ok", "plate": data.plate_text, "amount": session.amount}