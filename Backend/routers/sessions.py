from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from database import get_db

router = APIRouter()

@router.get("/paying")
def get_active_sessions(account_id: int, db: Session = Depends(get_db)):
    # Join Parked with Plate to filter by account_id
    active_sessions = db.query(models.Parked).join(models.Plate).filter(
        models.Plate.account_id == account_id,
        models.Parked.is_paid == False
    ).all()
    
    # Format the response to match the nested Parked schema
    formatted_sessions = []
    for session in active_sessions:
        plate = db.query(models.Plate).filter(models.Plate.plate_id == session.plate_id).first()
        parking = db.query(models.Parking).filter(models.Parking.parking_id == session.parking_id).first()
        
        formatted_sessions.append({
            "plate": plate,
            "parking": parking,
            "entry_time": session.entry_time.isoformat() if session.entry_time else None,
            "amount": session.amount,
            "is_paid": session.is_paid
        })
        
    return formatted_sessions