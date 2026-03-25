from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import ParkingSession, Parking
from schemas import SessionCreate, SessionResponse
from datetime import datetime

RATE = 2  # €/ora

router = APIRouter(prefix="/v1")


@router.post("/sessions/", response_model=SessionResponse)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    db_session = ParkingSession(
        plate_id   = session.plate_id,
        entry_time = datetime.now(),
        exit_time  = None,
        amount     = None,
        is_paid    = False,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    db_session = db.query(ParkingSession).filter(ParkingSession.id == session_id).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@router.get("/parking/current", response_model=SessionResponse)
def get_current_parking(plate_id: int, db: Session = Depends(get_db)):
    """Restituisce la sessione attiva (senza exit_time) per una targa."""
    db_session = db.query(ParkingSession).filter(
        ParkingSession.plate_id == plate_id,
        ParkingSession.exit_time == None
    ).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="No active session found")
    return db_session


@router.put("/sessions/{session_id}/exit", response_model=SessionResponse)
def exit_session(session_id: int, db: Session = Depends(get_db)):
    db_session = db.query(ParkingSession).filter(ParkingSession.id == session_id).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    db_session.exit_time = datetime.now()
    duration             = db_session.exit_time - db_session.entry_time
    hours                = duration.total_seconds() / 3600
    db_session.amount    = round(hours * RATE, 2)

    db.commit()
    db.refresh(db_session)
    return db_session
