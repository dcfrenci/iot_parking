from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import models, schemas
from database import get_db

router = APIRouter()

@router.get("/paying")
def get_active_sessions(account_id: int, db: Session = Depends(get_db)):
    active_sessions = db.query(models.Parked).join(models.Plate).filter(
        models.Plate.account_id == account_id,
        models.Parked.is_paid == False
    ).all()
    
    formatted_sessions = []
    for session in active_sessions:
        plate   = db.query(models.Plate).filter(models.Plate.plate_id == session.plate_id).first()
        parking = db.query(models.Parking).filter(models.Parking.parking_id == session.parking_id).first()
        
        formatted_sessions.append({
            "id":                 session.id,
            "plate":              plate,
            "parking":            parking,
            "entry_time":         session.entry_time.isoformat() if session.entry_time else None,
            "amount":             session.amount,
            "is_paid":            session.is_paid,
            "used_disabled_slot": session.used_disabled_slot
        })
        
    return formatted_sessions


@router.post("/paying")
def get_session_after_entry(data: schemas.SessionEntryCreate, db: Session = Depends(get_db)):
    db_plate = db.query(models.Plate).filter(
        models.Plate.plate_text == data.plate_number
    ).first()
    if not db_plate:
        raise HTTPException(status_code=404, detail="Plate not registered in the system")
    if db_plate.account_id != data.account_id:
        raise HTTPException(status_code=403, detail="Plate does not belong to the provided account")

    active_session = db.query(models.Parked).filter(
        models.Parked.plate_id == db_plate.plate_id,
        models.Parked.is_paid == False
    ).first()

    if not active_session:
        raise HTTPException(
            status_code=404,
            detail="No active session found. The vehicle must pass through the gate first."
        )

    return active_session

@router.delete("/paying")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session_to_delete = db.query(models.Parked).filter(
        models.Parked.id == session_id
    ).first()
    
    if not session_to_delete:
        raise HTTPException(status_code=404, detail="Session not found")

    # if session was still active, reset count
    if not session_to_delete.is_paid:
        parking = db.query(models.Parking).filter(
            models.Parking.parking_id == session_to_delete.parking_id
        ).first()
        if parking:
            if session_to_delete.used_disabled_slot:
                parking.available_disabled_slot = min(
                    parking.disabled_slot, parking.available_disabled_slot + 1
                )
            else:
                parking.available_slot = min(
                    parking.total_slot, parking.available_slot + 1
                )
        else:
            print(f"[WARN] delete_session: parking {session_to_delete.parking_id} not found")

    db.delete(session_to_delete)
    db.commit()
    return {"detail": "Session deleted successfully"}
