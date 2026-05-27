from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine
import models
from mqtt_client import mqtt_manager
from mqtt_handlers import on_mqtt_message
from routers import users, plates, parkings, bookings, sessions, gate, predictions

models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_manager.start(on_message_callback=on_mqtt_message)
    yield

app = FastAPI(title="IotParking API", version="0.2.0", lifespan=lifespan)

app.include_router(users.router,    prefix="/v1", tags=["Users & Auth"])
app.include_router(plates.router,   prefix="/v1", tags=["Plates"])
app.include_router(parkings.router, prefix="/v1", tags=["Parkings"])
app.include_router(bookings.router, prefix="/v1", tags=["Bookings"])
app.include_router(sessions.router, prefix="/v1", tags=["Active Sessions"])
app.include_router(gate.router,     prefix="/v1", tags=["Gate"])
app.include_router(predictions.router, prefix="/v1", tags=["Predictions"])