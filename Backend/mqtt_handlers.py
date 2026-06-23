import os
import models
from database import SessionLocal

PARKING_ID = int(os.getenv("PARKING_ID", 1))

def process_disabled_slot_update(db, parking_id: int, payload: str) -> None:
    parking = db.query(models.Parking).filter(
        models.Parking.parking_id == parking_id
    ).first()
    if not parking:
        print(f"[mqtt] Parking {parking_id} not found, ignoring message")
        return

    active_gate_session = db.query(models.Parked).filter(
        models.Parked.parking_id == parking_id,
        models.Parked.used_disabled_slot == True,
        models.Parked.is_paid == False
    ).first()

    if payload == "OCCUPIED":
        if active_gate_session:
            print("[mqtt] OCCUPIED received on active session — counter OK")
            return
        if parking.available_disabled_slot > 0:
            parking.available_disabled_slot -= 1
            db.commit()
            print(f"[mqtt] disabled slot occupied without gate — available_disabled_slot → {parking.available_disabled_slot}")
        else:
            print("[mqtt] OCCUPIED received but available_disabled_slot is set to 0")

    elif payload == "FREE":
        if active_gate_session:
            print("[mqtt] FREE received but session still active — counter OK")
            return
        parking.available_disabled_slot = min(
            parking.disabled_slot,
            parking.available_disabled_slot + 1
        )
        db.commit()
        print(f"[mqtt] Free disabled spot without gate — available_disabled_slot → {parking.available_disabled_slot}")

    else:
        print(f"[mqtt] unknown payload on topic parking/disabled: '{payload}'")

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