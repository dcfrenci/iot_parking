from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="IoT Parking Mock API")
router = APIRouter(prefix="/v1")

# ─── Pydantic Models ──────────────────────────────────────────────────────────

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
    name: str
    parking_id: str
    parking_name: str
    date: str
    car_plate: str
    slot_code: str
    days: int
    price_per_hour: float

class CreateBookingDto(BaseModel):
    name: str
    parking_id: str
    car_plate: str
    days: int

class UpdateBookingPlateDto(BaseModel):
    car_plate: str

class CurrentParkingDto(BaseModel):
    parking_name: str
    car_plate: str
    price_per_hour: float
    started_at: str
    latitude: float
    longitude: float

class UserDto(BaseModel):
    id: str
    name: str
    email: str

class PlateDto(BaseModel):
    id: str
    name: str
    plate_text: str
    is_active: bool
    image_uri: Optional[str] = None

class CreatePlateDto(BaseModel):
    name: str
    plate_text: str
    image_uri: Optional[str] = None

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
        ParkingDto(
            id="p1", name="Central Station Parking", address="Piazza Dante 1",
            latitude=44.6471, longitude=10.9252,
            available_slots=12, total_slots=50, price_per_hour=2.50, distance_km=0.8
        ),
        ParkingDto(
            id="p2", name="City Center Garage", address="Via Emilia Centro 100",
            latitude=44.6460, longitude=10.9255,
            available_slots=3, total_slots=20, price_per_hour=3.00, distance_km=1.2
        ),
    ],
    "current_parking": CurrentParkingDto(
        parking_name="Central Station Parking",
        car_plate="AB123CD",
        price_per_hour=2.50,
        started_at="2026-03-23T18:00:00Z",
        latitude=44.6471,
        longitude=10.9252,
    ),
    "bookings": [
        BookingDto(
            id="b1", name="Weekend trip", parking_id="p2",
            parking_name="City Center Garage", date="2026-03-20T10:00:00Z",
            car_plate="AB123CD", slot_code="A12", days=2, price_per_hour=3.00
        ),
        BookingDto(
            id="b2", name="Airport stay", parking_id="p1",
            parking_name="Central Station Parking", date="2026-02-15T08:00:00Z",
            car_plate="XY987ZT", slot_code="C45", days=5, price_per_hour=2.50
        ),
    ],
    "user": UserDto(id="u1", name="Mario Rossi", email="mario.rossi@example.com"),
    "plates": [
        PlateDto(id="pl1", name="My Car",     plate_text="AB123CD", is_active=True,  image_uri=None),
        PlateDto(id="pl2", name="Wife's Car", plate_text="XY987ZT", is_active=False, image_uri=None),
    ],
    "payment_method": PaymentMethodDto(id="pm1", last_four="4242", brand="Visa"),
    "preferences": ParkingPreferencesDto(max_distance_km=5.0, max_price_per_hour=4.50),
}

# ─── Parking Endpoints ────────────────────────────────────────────────────────

@router.get("/parkings", response_model=List[ParkingDto])
def get_nearby_parkings(lat: float, lon: float):
    return DB["parkings"]

@router.get("/parking/current", response_model=Optional[CurrentParkingDto])
def get_current_parking():
    return DB["current_parking"]

# ─── Booking Endpoints ────────────────────────────────────────────────────────

@router.get("/bookings", response_model=List[BookingDto])
def get_bookings():
    return DB["bookings"]

@router.post("/bookings", response_model=BookingDto, status_code=201)
def create_booking(body: CreateBookingDto):
    parking = next((p for p in DB["parkings"] if p.id == body.parking_id), None)
    if parking is None:
        raise HTTPException(status_code=404, detail="Parking not found")

    # Assign the next available slot code
    existing_slots = {b.slot_code for b in DB["bookings"]}
    slot_letter = chr(ord("A") + len(DB["bookings"]) // 10)
    slot_number = len(DB["bookings"]) % 10 + 1
    slot_code = f"{slot_letter}{slot_number:02d}"
    while slot_code in existing_slots:
        slot_number += 1
        slot_code = f"{slot_letter}{slot_number:02d}"

    new_booking = BookingDto(
        id           = str(uuid.uuid4())[:8],
        name         = body.name,
        parking_id   = body.parking_id,
        parking_name = parking.name,
        date         = "2026-03-24T12:00:00Z",
        car_plate    = body.car_plate,
        slot_code    = slot_code,
        days         = body.days,
        price_per_hour = parking.price_per_hour,
    )
    DB["bookings"].append(new_booking)
    return new_booking

@router.patch("/bookings/{booking_id}", response_model=BookingDto)
def update_booking_plate(booking_id: str, body: UpdateBookingPlateDto):
    for i, booking in enumerate(DB["bookings"]):
        if booking.id == booking_id:
            # Validate plate exists
            plate_exists = any(p.plate_text == body.car_plate for p in DB["plates"])
            if not plate_exists:
                raise HTTPException(status_code=400, detail="Plate not registered")
            updated = booking.model_copy(update={"car_plate": body.car_plate})
            DB["bookings"][i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Booking not found")

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

@router.post("/user/plates", response_model=PlateDto, status_code=201)
def add_plate(body: CreatePlateDto):
    # Check for duplicate plate text
    if any(p.plate_text == body.plate_text for p in DB["plates"]):
        raise HTTPException(status_code=409, detail="Plate already registered")
    new_plate = PlateDto(
        id        = f"pl{len(DB['plates']) + 1}",
        name      = body.name,
        plate_text = body.plate_text,
        is_active = False,
        image_uri = body.image_uri,
    )
    DB["plates"].append(new_plate)
    return new_plate

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