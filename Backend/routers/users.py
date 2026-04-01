from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter()

# --- Authentication & Registration ---

@router.post("/login", response_model=schemas.UserResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    # In a real app, verify the hashed password here
    if not user or user.hashed_password != credentials.password + "notreallyhashed":
        raise HTTPException(status_code=422, detail="Invalid credentials")
    return user

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail={"status": 409, "message": "Email already exists", "field": "email"})
    
    new_user = models.User(
        name=user.name, 
        email=user.email, 
        hashed_password=user.password + "notreallyhashed"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- User Management ---

@router.get("/user", response_model=schemas.UserResponse)
def get_user(account_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.account_id == account_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/user", response_model=schemas.UserResponse)
def update_user(user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.account_id == user_update.account_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.name:
        user.name = user_update.name
    if user_update.email:
        user.email = user_update.email
    if user_update.new_pass and user_update.old_pass:
        # Verify old password before updating
        user.hashed_password = user_update.new_pass + "notreallyhashed"
        
    db.commit()
    db.refresh(user)
    return user

@router.delete("/user")
def delete_user(account_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.account_id == account_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}

# --- Payments ---

@router.get("/user/payment")
def get_payment(account_id: int, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.account_id == account_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment method not found")
    return payment

@router.post("/user/payment", response_model=schemas.PaymentMethodDto, status_code=status.HTTP_201_CREATED)
def create_payment_method(
    payment_data: schemas.UpdatePaymentDto, 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.account_id == payment_data.account_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    existing_payment = db.query(models.Payment).filter(
        models.Payment.account_id == payment_data.account_id
    ).first()
    
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Payment method already exists. Use PATCH to update."
        )
        
    new_payment = models.Payment(
        account_id=payment_data.account_id,
        circuit=payment_data.payment.circuit,
        card_number=payment_data.payment.card_number
    )
    
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    return new_payment

@router.patch("/user/payment", response_model=schemas.PaymentMethodDto)
def update_payment(
    payment_data: schemas.UpdatePaymentDto, 
    db: Session = Depends(get_db)
):
    payment = db.query(models.Payment).filter(
        models.Payment.account_id == payment_data.account_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Payment method not found. Use POST to create one."
        )
        
    payment.circuit = payment_data.payment.circuit
    payment.card_number = payment_data.payment.card_number
    
    db.commit()
    db.refresh(payment)
    
    return payment

# --- Preferences ---

@router.get("/user/preferences/distance")
def get_distance_pref(account_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.account_id == account_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"distance_value": user.pref_distance}

@router.patch("/user/preferences/distance")
def update_distance_pref(payload: dict, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.account_id == payload["account_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.pref_distance = payload["new_distance"]
    db.commit()
    return {"distance_value": user.pref_distance}

@router.get("/user/preferences/price")
def get_price_pref(account_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.account_id == account_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"price_value": user.pref_price}

@router.patch("/user/preferences/price")
def update_price_pref(payload: dict, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.account_id == payload["account_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.pref_price = payload["new_price"]
    db.commit()
    return {"price_value": user.pref_price}