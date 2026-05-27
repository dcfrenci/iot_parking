from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import models, schemas
from database import get_db

router = APIRouter()

@router.get("/parkings/{parking_id}/predictions")
def get_predictions(parking_id: int, target_date: str, db: Session = Depends(get_db)):
    
    parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    
    start_of_day = datetime.combine(parsed_date, datetime.min.time())
    end_of_day = datetime.combine(parsed_date, datetime.max.time())
    

    predictions = db.query(models.Predictions).filter(
        models.Predictions.parking_id == parking_id,
        models.Predictions.timestamp.between(start_of_day, end_of_day)
    ).order_by(models.Predictions.timestamp.asc()).all()
    
    if not predictions:
        raise HTTPException(status_code=404, detail="No predictions available for this date")
    
    
    formatted_predictions = []
    for pred in predictions:
        formatted_predictions.append({
            "id": pred.id,
            "parking_id": pred.parking_id,

            "timestamp": pred.timestamp.isoformat() if pred.timestamp else None,
            "occupied_slots": pred.occupied_slots,
            "disabled_occupied_slots": pred.disabled_occupied_slots
        })
        
    return formatted_predictions


@router.post("/parkings/{parking_id}/history", status_code=201)
def upload_parking_history(parking_id: int, history_data: list[schemas.ParkingHistoryCreate], db: Session = Depends(get_db)):
    
    parking = db.query(models.Parking).filter(models.Parking.parking_id == parking_id).first()
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
        
    
    db.query(models.ParkinHistory).filter(models.ParkinHistory.parking_id == parking_id).delete()
    
    db_records = []
    for item in history_data:
        dt_obj = datetime.fromisoformat(item.timestamp)
        
        db_records.append(
            models.ParkinHistory(
                parking_id=parking_id,
                timestamp=dt_obj,
                occupied_slots=item.occupied_slots,
                disabled_occupied_slots=item.disabled_occupied_slots
            )
        )
        
    # Inserimento di massa super veloce
    db.bulk_save_objects(db_records)
    db.commit()
    
    return {"detail": f"Successfully uploaded {len(db_records)} history records"}