import os
import models
from database import SessionLocal

PARKING_ID = int(os.getenv("PARKING_ID", 1))

def process_disabled_slot_update(db, parking_id: int, payload: str):
    parking = db.query(models.Parking).filter(models.Parking.parking_id == parking_id).first()
    if not parking:
        return

    active_session = db.query(models.Parked).filter(
        models.Parked.parking_id == parking_id,
        models.Parked.used_disabled_slot == True,
        models.Parked.is_paid == False
    ).first()

    if payload == "OCCUPIED" and not active_session:
        parking.available_disabled_slot = max(0, parking.available_disabled_slot - 1)
        db.commit()
    elif payload == "FREE" and active_session:
        parking.available_disabled_slot = min(parking.disabled_slot, parking.available_disabled_slot + 1)
        db.commit()

def on_mqtt_message(client, userdata, msg):
    if msg.topic == "parking/disabled":
        payload = msg.payload.decode("utf-8").strip()
        db = SessionLocal()
        try:
            process_disabled_slot_update(db, PARKING_ID, payload)
        except Exception:
            db.rollback()
        finally:
            db.close()