from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Plate
from schemas import PlateResponse

router = APIRouter(prefix="/v1")


@router.get("/plates/{plate_id}", response_model=PlateResponse)
def get_plate(plate_id: int, db: Session = Depends(get_db)):
    db_plate = db.query(Plate).filter(Plate.id == plate_id).first()
    if db_plate is None:
        raise HTTPException(status_code=404, detail="Plate not found")
    return db_plate


@router.get("/plates/{plate_text}/check")
def check_plate(plate_text: str, db: Session = Depends(get_db)):
    db_plate = db.query(Plate).filter(Plate.plate_text == plate_text).first()
    if db_plate is None:
        raise HTTPException(status_code=404, detail="Plate not found")
    if not db_plate.is_active:
        raise HTTPException(status_code=403, detail="Plate not authorized")
    return {"authorized": True}
