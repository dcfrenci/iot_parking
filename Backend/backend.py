from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="IoT Parking Mock API")
router = APIRouter(prefix="/v1")

# ─── Pydantic Models (Matching your Kotlin DTOs) ──────────────────────────────

class ParkingDto(BaseModel):
    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    available_slots: int
    total_slots: int
    price_per_hour: float
    distance_km: float

class BookingDto(BaseModel):
    id: str
    parking_name: str
    date: str
    car_plate: str
    slot_code: str

class CurrentParkingDto(BaseModel):
    parking_name: str
    car_plate: str
    price_per_hour: float
    started_at: str

class UserDto(BaseModel):
    id: str
    name: str
    email: str

class PlateDto(BaseModel):
    id: str
    name: str
    plate_text: str
    is_active: bool

class PlateActiveUpdate(BaseModel):
    is_active: bool

class PaymentMethodDto(BaseModel):
    id: str
    last_four: str
    brand: str

class ParkingPreferencesDto(BaseModel):
    max_distance_km: float
    max_price_per_hour: float

# ─── In-Memory Database ───────────────────────────────────────────────────────

DB = {
    "parkings": [
        ParkingDto(id="p1", name="Central Station Parking", address="Piazza Dante 1", latitude=44.6471, longitude=10.9252, available_slots=12, total_slots=50, price_per_hour=2.50, distance_km=0.8),
        ParkingDto(id="p2", name="City Center Garage", address="Via Emilia Centro 100", latitude=44.6460, longitude=10.9255, available_slots=3, total_slots=20, price_per_hour=3.00, distance_km=1.2)
    ],
    "current_parking": CurrentParkingDto(parking_name="Central Station Parking", car_plate="AB123CD", price_per_hour=2.50, started_at="2026-03-23T18:00:00Z"),
    "bookings": [
        BookingDto(id="b1", parking_name="City Center Garage", date="2026-03-20T10:00:00Z", car_plate="AB123CD", slot_code="A12"),
        BookingDto(id="b2", parking_name="Airport Long Stay", date="2026-02-15T08:00:00Z", car_plate="XY987ZT", slot_code="C45")
    ],
    "user": UserDto(id="u1", name="Mario Rossi", email="mario.rossi@example.com"),
    "plates": [
        PlateDto(id="pl1", name="My Car", plate_text="AB123CD", is_active=True),
        PlateDto(id="pl2", name="Wife's Car", plate_text="XY987ZT", is_active=False)
    ],
    "payment_method": PaymentMethodDto(id="pm1", last_four="4242", brand="Visa"),
    "preferences": ParkingPreferencesDto(max_distance_km=5.0, max_price_per_hour=4.50)
}

# ─── Parking Endpoints ────────────────────────────────────────────────────────

@router.get("/parkings", response_model=List[ParkingDto])
def get_nearby_parkings(lat: float, lon: float):
    # In a real app, you would filter by coordinates. Here we return the mock list.
    return DB["parkings"]

@router.get("/parking/current", response_model=Optional[CurrentParkingDto])
def get_current_parking():
    return DB["current_parking"]

@router.get("/bookings", response_model=List[BookingDto])
def get_bookings():
    return DB["bookings"]

# ─── Settings Endpoints ───────────────────────────────────────────────────────

@router.get("/user", response_model=UserDto)
def get_user():
    return DB["user"]

@router.get("/user/plates", response_model=List[PlateDto])
def get_plates():
    return DB["plates"]

@router.patch("/user/plates/{plate_id}")
def set_plate_active(plate_id: str, update: PlateActiveUpdate):
    for plate in DB["plates"]:
        if plate.id == plate_id:
            plate.is_active = update.is_active
            return {"status": "success"}
    raise HTTPException(status_code=404, detail="Plate not found")

@router.get("/user/payment", response_model=PaymentMethodDto)
def get_payment_method():
    return DB["payment_method"]

@router.get("/user/preferences", response_model=ParkingPreferencesDto)
def get_preferences():
    return DB["preferences"]

@router.put("/user/preferences")
def save_preferences(prefs: ParkingPreferencesDto):
    DB["preferences"] = prefs
    return {"status": "success"}

app.include_router(router)