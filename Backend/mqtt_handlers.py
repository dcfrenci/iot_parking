import os
import models
from database import SessionLocal

PARKING_ID = int(os.getenv("PARKING_ID", 1))

def process_disabled_slot_update(db, parking_id: int, payload: str) -> None:
    parking = db.query(models.Parking).filter(
        models.Parking.parking_id == parking_id
    ).first()
    
    if not parking:
        print(f"[mqtt] Parking {parking_id} not found")
        return

    active_sessions = db.query(models.Parked).filter(
        models.Parked.parking_id == parking_id,
        models.Parked.used_disabled_slot == True,
        models.Parked.is_paid == False
    ).count()

    if payload == "OCCUPIED":
        if active_sessions == 0:
            print("[mqtt] Occupied disabled slot with NO active session")
            
            if parking.available_disabled_slot > 0:
                parking.available_disabled_slot -= 1
                db.commit()
        else:
            print(f"[mqtt] Disabled slot occupied WITH active session (total active: {active_sessions})")

    elif payload == "FREE":
        if active_sessions == 0:
            parking.available_disabled_slot = min(parking.disabled_slot, parking.available_disabled_slot + 1)
            db.commit()
            print(f"[mqtt] Disabled slot Free WITH available_disabled_slot → {parking.available_disabled_slot}")
        else:
            print(f"[mqtt] Disabled slot Free but {active_sessions} sessions still active in DB")

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