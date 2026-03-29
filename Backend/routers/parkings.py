from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter()

@router.get("/parkings/all")
def get_all_parkings_summary(db: Session = Depends(get_db)):
    parkings = db.query(models.Parking.parking_id, models.Parking.parking_name, models.Parking.address).all()
    return [{"parking_id": p.parking_id, "parking_name": p.parking_name, "address": p.address} for p in parkings]

@router.get("/parkings", response_model=schemas.ParkingResponse)
def get_parking(parking_id: int, db: Session = Depends(get_db)):
    parking = db.query(models.Parking).filter(models.Parking.parking_id == parking_id).first()
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    return parking

@router.post("/parkings", response_model=schemas.ParkingResponse, status_code=status.HTTP_201_CREATED)
def create_parking(payload: dict, db: Session = Depends(get_db)):
    parking_data = payload.get("parking")
    new_parking = models.Parking(**parking_data)
    db.add(new_parking)
    db.commit()
    db.refresh(new_parking)
    return new_parking

@router.patch("/parkings", response_model=schemas.ParkingResponse)
def update_parking(payload: dict, db: Session = Depends(get_db)):
    parking_data = payload.get("parking")
    parking_id = parking_data.get("parking_id")
    
    parking = db.query(models.Parking).filter(models.Parking.parking_id == parking_id).first()
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
        
    for key, value in parking_data.items():
        setattr(parking, key, value)
        
    db.commit()
    db.refresh(parking)
    return parking

@router.delete("/parkings")
def delete_parking(parking_id: int, db: Session = Depends(get_db)):
    parking = db.query(models.Parking).filter(models.Parking.parking_id == parking_id).first()
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    db.delete(parking)
    db.commit()
    return {"detail": "Parking deleted"}

@router.get("/parkings/range")
def get_parkings_in_range(lat: float, lon: float, range: int, db: Session = Depends(get_db)):
    # Basic bounding box or haversine formula should be implemented here
    # This is a mocked example returning all parkings for simplicity
    parkings = db.query(models.Parking).all()
    results = []
    for p in parkings:
        # Calculate actual distance here
        mock_distance = 2.5 
        if mock_distance <= range:
            results.append({"parking": p, "distance": mock_distance})
    return results