from fastapi import FastAPI
from routers import users, plates, parkings, bookings, sessions
from database import engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="IotParking API", version="0.1.9")

# Register the routers
app.include_router(users.router, prefix="/v1", tags=["Users & Auth"])
app.include_router(plates.router, prefix="/v1", tags=["Plates"])
app.include_router(parkings.router, prefix="/v1", tags=["Parkings"])
app.include_router(bookings.router, prefix="/v1", tags=["Bookings"])
app.include_router(sessions.router, prefix="/v1", tags=["Active Sessions"])