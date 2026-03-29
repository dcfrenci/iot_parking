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

# --- Plate Schemas ---
class PlateCreate(BaseModel):
    account_id: int
    plate_text: str
    plate_name: str
    image_uri: str

class PlateResponse(BaseModel):
    plate_id: int
    plate_text: str
    plate_name: str
    is_active: bool
    image_uri: str
    
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