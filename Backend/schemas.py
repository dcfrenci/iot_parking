from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, date

# --- User Schemas ---
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(alias='pass')

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(alias='pass')

class UserUpdate(BaseModel):
    account_id: int
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    new_pass: Optional[str] = None
    old_pass: Optional[str] = None

class UserResponse(BaseModel):
    account_id: int
    name: str
    email: EmailStr
    
    class Config:
        orm_mode = True

class SessionEntryCreate(BaseModel):
    account_id: int
    parking_id: int
    plate_number: str

# --- Preferences Schemas ---
class DistancePreferenceDto(BaseModel):
    distance_value: float

class UpdateDistancePreferenceDto(BaseModel):
    account_id: int
    distance_value: float

class PricePreferenceDto(BaseModel):
    price_value: float

class UpdatePricePreferenceDto(BaseModel):
    account_id: int
    price_value: float

# --- Payment Schemas ---
class PaymentMethodDto(BaseModel):
    circuit: str
    card_number: str

    class Config:
        orm_mode = True

class UpdatePaymentDto(BaseModel):
    account_id: int
    payment: PaymentMethodDto

# --- Plate Schemas ---
class PlateCreate(BaseModel):
    account_id: int
    plate_text: str
    plate_name: str
    image_uri: Optional[str] = ""

class PlateResponse(BaseModel):
    plate_id: int
    plate_text: str
    plate_name: str
    is_active: bool
    image_uri: Optional[str] = None
    
    class Config:
        orm_mode = True

# --- Parking Schemas ---
class ParkingBase(BaseModel):
    parking_name: str
    total_slot: int
    available_slot: int
    price_per_hour: float
    lat: float
    lon: float
    address: str

class ParkingResponse(ParkingBase):
    parking_id: int
    
    class Config:
        orm_mode = True

# --- Booking Schemas ---
class BookingResponse(BaseModel):
    booking_id: int
    booking_name: str
    parking: ParkingResponse
    plate: PlateResponse
    date: date
    days: int
    slot_code: int
    
    class Config:
        orm_mode = True

# --- Gate Schemas ---
class GateEntryRequest(BaseModel):
    plate_text: str

class GateExitRequest(BaseModel):
    plate_text: str