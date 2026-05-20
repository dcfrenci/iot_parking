from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import models, schemas
from database import get_db
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
from sqlalchemy import update

load_dotenv()

router = APIRouter()

PARKING_ID = int(os.getenv("PARKING_ID", 1))
MQTT_BROKER = os.getenv("MQTT_BROKER", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

# Client
_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="fastapi_gate")
_mqtt.connect(MQTT_BROKER, MQTT_PORT)
_mqtt.loop_start()

def publish(topic: str, payload: str):
    msg = _mqtt.publish(topic, payload, qos=1)
    msg.wait_for_publish(timeout=2)



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
    
    # Verify if disabled user
    user = db.query(models.User).filter(
        models.User.account_id == plate.account_id
    ).first()
    use_disabled = user.is_disabled if user else False

    parking = db.query(models.Parking).filter(models.Parking.parking_id == PARKING_ID).first()
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    
    # Number of slots update
    if use_disabled:
        if parking.available_disabled_slot <= 0:
            raise HTTPException(status_code=403, detail="No disabled slots available")
        parking.available_disabled_slot -= 1
    else:
        if parking.available_slot <= 0:
            raise HTTPException(status_code=403, detail="No available slots")
        parking.available_slot -= 1


    new_session = models.Parked(
        plate_id=plate.plate_id,
        parking_id=PARKING_ID,
        entry_time=datetime.now(),
        amount=0.0,
        is_paid=False,
        used_disabled_slot=use_disabled
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    publish("parking/gate/entry", "o1")

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


    parking = db.query(models.Parking).filter(models.Parking.parking_id == PARKING_ID).first()
    duration = (datetime.now() - session.entry_time).total_seconds() / 3600
    session.amount = round(duration * parking.price_per_hour, 2)
    session.is_paid = True

    if session.used_disabled_slot:
        parking.available_disabled_slot = min(
            parking.disabled_slot, parking.available_disabled_slot + 1
        )
    else:
        parking.available_slot = min(
            parking.total_slot, parking.available_slot + 1
        )

    db.commit()

    publish("parking/gate/exit", "o2")

    return {"status": "ok", "plate": data.plate_text, "amount": session.amount}