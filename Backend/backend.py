from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import users, plates, parkings, bookings, sessions, gate
from database import engine, SessionLocal
import models
import paho.mqtt.client as mqtt
import threading
import os
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

PARKING_ID  = int(os.getenv("PARKING_ID", 1))
MQTT_BROKER = os.getenv("MQTT_BROKER", "127.0.0.1")
MQTT_PORT   = int(os.getenv("MQTT_PORT", 1883))


# Disabled spot handler
def handle_disabled_spot(payload: str):
    db = SessionLocal()
    try:
        parking = db.query(models.Parking).filter(
            models.Parking.parking_id == PARKING_ID
        ).first()
        if not parking:
            return

        if payload == "OCCUPIED":
            active_h = db.query(models.Parked).filter(
                models.Parked.parking_id == PARKING_ID,
                models.Parked.used_disabled_slot == True,
                models.Parked.is_paid == False
            ).first()

            if not active_h:
                print(f"[WARN] Disabled slot occupied without active session")
                parking.available_disabled_slot = max(0, parking.available_disabled_slot - 1)
                db.commit()
            else:
                # Sessione già registrata correttamente dal gate, niente da fare
                print(f"[mqtt] already existing session")

        elif payload == "FREE":
            active_h = db.query(models.Parked).filter(
                models.Parked.parking_id == PARKING_ID,
                models.Parked.used_disabled_slot == True,
                models.Parked.is_paid == False
            ).first()

            if active_h:
                print(f"[WARN] Free disabled slot with active session")
                parking.available_disabled_slot = min(
                    parking.disabled_slot, parking.available_disabled_slot + 1
                )
                db.commit()
            else:
                print(f"[mqtt] free disabled spot")

    except Exception as e:
        print(f"[mqtt] Errore handle_disabled_spot: {e}")
        db.rollback()
    finally:
        db.close()


def on_message(client, userdata, msg):
    topic   = msg.topic
    payload = msg.payload.decode("utf-8").strip()

    if topic == "parking/disabled":
        handle_disabled_spot(payload)


def start_mqtt_subscriber():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="fastapi_subscriber")
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe("parking/disabled", qos=1)
    client.loop_forever()


@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=start_mqtt_subscriber, daemon=True)
    thread.start()
    print("[mqtt] Subscriber started")
    yield


app = FastAPI(title="IotParking API", version="0.2.0", lifespan=lifespan)

app.include_router(users.router,    prefix="/v1", tags=["Users & Auth"])
app.include_router(plates.router,   prefix="/v1", tags=["Plates"])
app.include_router(parkings.router, prefix="/v1", tags=["Parkings"])
app.include_router(bookings.router, prefix="/v1", tags=["Bookings"])
app.include_router(sessions.router, prefix="/v1", tags=["Active Sessions"])
app.include_router(gate.router,     prefix="/v1", tags=["Gate"])
