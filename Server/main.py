from fastapi import FastAPI
from database import Base, engine
from routers.users import router as users_router
from routers.plates import router as plates_router
from routers.sessions import router as sessions_router
from routers.parkings import router as parkings_router
from routers.bookings import router as bookings_router

app = FastAPI(title="IoT Parking API")

Base.metadata.create_all(bind=engine)

app.include_router(users_router)
app.include_router(plates_router)
app.include_router(sessions_router)
app.include_router(parkings_router)
app.include_router(bookings_router)
