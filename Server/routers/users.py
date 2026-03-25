from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Plate
from schemas import UserCreate, UserResponse, PlateResponse, PlateCreate, PlateActiveUpdate, UserLogin
from security import hash_password, verify_password

router = APIRouter(prefix="/v1")


@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email, password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/user", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/user/plates", response_model=list[PlateResponse])
def get_plates(user_id: int, db: Session = Depends(get_db)):
    return db.query(Plate).filter(Plate.user_id == user_id).all()


@router.post("/user/plates", response_model=PlateResponse, status_code=201)
def add_plate(plate: PlateCreate, db: Session = Depends(get_db)):
    existing = db.query(Plate).filter(Plate.plate_text == plate.plate_text).first()
    if existing:
        raise HTTPException(status_code=409, detail="Plate already registered")
    db_plate = Plate(
        name      = plate.name,
        plate_text = plate.plate_text,
        is_active  = False,
        image_uri  = plate.image_uri,
        user_id    = plate.user_id,
    )
    db.add(db_plate)
    db.commit()
    db.refresh(db_plate)
    return db_plate


@router.patch("/user/plates/{plate_id}")
def set_plate_active(plate_id: int, update: PlateActiveUpdate, db: Session = Depends(get_db)):
    db_plate = db.query(Plate).filter(Plate.id == plate_id).first()
    if db_plate is None:
        raise HTTPException(status_code=404, detail="Plate not found")
    db_plate.is_active = update.is_active
    db.commit()
    return {"status": "success"}


@router.post("/login/", response_model=UserResponse)
def login(login: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == login.email).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Invalid credentials")
    
    if not verify_password(login.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return db_user
    
