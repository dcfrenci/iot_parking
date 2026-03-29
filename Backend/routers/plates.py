from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter()

@router.get("/user/plates", response_model=List[schemas.PlateResponse])
def get_user_plates(account_id: int, db: Session = Depends(get_db)):
    plates = db.query(models.Plate).filter(models.Plate.account_id == account_id).all()
    return plates

@router.post("/user/plates", response_model=schemas.PlateResponse, status_code=status.HTTP_201_CREATED)
def create_plate(plate: schemas.PlateCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Plate).filter(models.Plate.plate_text == plate.plate_text).first()
    if existing:
        raise HTTPException(status_code=409, detail={"status": 409, "message": "Plate already registered", "field": "plate_text"})
    
    new_plate = models.Plate(**plate.dict())
    db.add(new_plate)
    db.commit()
    db.refresh(new_plate)
    return new_plate

@router.delete("/user/plates")
def delete_plate(account_id: int, plate_id: int, db: Session = Depends(get_db)):
    plate = db.query(models.Plate).filter(
        models.Plate.account_id == account_id,
        models.Plate.plate_id == plate_id
    ).first()
    
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")
        
    db.delete(plate)
    db.commit()
    return {"detail": "Plate deleted successfully"}