from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Parking
from schemas import ParkingCreate, ParkingResponse
import math

router = APIRouter(prefix="/v1")


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcola la distanza in km tra due coordinate geografiche."""
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return round(R * 2 * math.asin(math.sqrt(a)), 2)


@router.get("/parkings", response_model=list[ParkingResponse])
def get_nearby_parkings(lat: float, lon: float, db: Session = Depends(get_db)):
    parkings = db.query(Parking).all()
    result = []
    for p in parkings:
        p_dict = {
            "id": p.id, "name": p.name, "address": p.address,
            "latitude": p.latitude, "longitude": p.longitude,
            "available_slots": p.available_slots, "total_slots": p.total_slots,
            "price_per_hour": p.price_per_hour,
            "distance_km": haversine(lat, lon, p.latitude, p.longitude),
        }
        result.append(p_dict)
    return result


@router.post("/parkings", response_model=ParkingResponse, status_code=201)
def create_parking(parking: ParkingCreate, db: Session = Depends(get_db)):
    db_parking = Parking(**parking.model_dump())
    db.add(db_parking)
    db.commit()
    db.refresh(db_parking)
    return db_parking


# TODO It's just a mockup
@router.get("/parking/current")
def get_current_parking(user_id: int = 1):
    return {
        "parking_name": "Central Station Parking",
        "car_plate": "AB123CD",
        "price_per_hour": 2.50,
        "started_at": "2026-03-23T18:00:00Z",
        "latitude": 44.6471,
        "longitude": 10.9252,
    }