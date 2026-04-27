from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import models, schemas
from database import get_db
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

PARKING_ID = int(os.getenv("PARKING_ID", 1))
MQTT_BROKER = os.getenv("MQTT_BROKER", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

print(f"[config] PARKING_ID={PARKING_ID}, BROKER={MQTT_BROKER}:{MQTT_PORT}")

@router.post("/gate/entry")
def gate_entry(data: schemas.GateEntryRequest, db: Session = Depends(get_db)):

    plate = db.query(models.Plate).filter(models.Plate.plate_text == data.plate_text).first()
    
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not registered")
    
    if not plate.is_active:
        raise HTTPException(status_code=403, detail="Plate is not active")
    

    # payment = db.query(models.Payment).filter(models.Payment.account_id == plate.account_id).first()

    # if not payment:
    #     raise HTTPException(status_code=403, detail="No payment method registered")


    # parking = db.query(models.Parking).filter(models.Parking.parking_id == PARKING_ID).first()
    
    # if not parking:
    #     raise HTTPException(status_code=404, detail="Parking not found")

    # if parking.available_slot == 0:
    #     raise HTTPException(status_code=403, detail="No available slots")

    # parking.available_slot -= 1
    # db.commit()


    new_session = models.Parked(
        plate_id=plate.plate_id,
        parking_id=PARKING_ID,
        entry_time=datetime.now(),
        amount=0.0,
        is_paid=False
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)


    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect(MQTT_BROKER, MQTT_PORT)
    mqttc.loop_start()

    msg_info = mqttc.publish("parking/gate/entry", "open", qos=1)
    msg_info.wait_for_publish(timeout=1)

    mqttc.loop_stop()
    mqttc.disconnect()



    
    return {"status": "ok", "plate": data.plate_text}



@router.post("/gate/exit")
def gate_exit(data: schemas.GateExitRequest, db: Session = Depends(get_db)):

    plate = db.query(models.Plate).filter(models.Plate.plate_text == data.plate_text).first()

    if not plate:
        raise HTTPException(status_code=404, detail="Plate not registered")
    
    if not plate.is_active:
        raise HTTPException(status_code=403, detail="Plate is not active")
    
    session = db.query(models.Parked).filter(models.Parked.plate_id == plate.plate_id, 
                                             models.Parked.is_paid == False).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")
    
    parking = db.query(models.Parking).filter(models.Parking.parking_id == PARKING_ID).first()
    duration = (datetime.now() - session.entry_time).seconds / 3600
    session.amount = round(duration * parking.price_per_hour, 2)
    session.is_paid = True

    parking.available_slot += 1
    db.commit()

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect(MQTT_BROKER, MQTT_PORT)
    mqttc.loop_start()

    msg_info = mqttc.publish("parking/gate/exit", "open", qos=1)
    msg_info.wait_for_publish(timeout=1)

    mqttc.loop_stop()
    mqttc.disconnect()
    
    return {"status": "ok", "plate": data.plate_text, "amount": session.amount}
    

