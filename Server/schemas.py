from pydantic import BaseModel
from typing import Optional
from datetime import datetime


### USER ###

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


### LOGIN ###

class UserLogin(BaseModel):
    email: str
    password: str


### PLATE ###

class PlateBase(BaseModel):
    name: str
    plate_text: str
    is_active: bool
    image_uri: Optional[str] = None

class PlateCreate(PlateBase):
    user_id: int

class PlateResponse(PlateBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class PlateActiveUpdate(BaseModel):
    is_active: bool


### PARKING ###

class ParkingBase(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    available_slots: int
    total_slots: int
    price_per_hour: float

class ParkingCreate(ParkingBase):
    pass

class ParkingResponse(ParkingBase):
    id: int
    distance_km: Optional[float] = None   # calcolato a runtime, non in DB

    class Config:
        from_attributes = True


### BOOKING ###

class BookingBase(BaseModel):
    name: str
    parking_id: int
    car_plate: str
    days: int

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: int
    date: datetime
    slot_code: str
    price_per_hour: float
    parking_name: str
    user_id: int

    class Config:
        from_attributes = True

class UpdateBookingPlateDto(BaseModel):
    car_plate: str


### SESSION ###

class SessionBase(BaseModel):
    plate_id: int
    parking_id: int

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: int
    entry_time: datetime
    exit_time: Optional[datetime] = None
    amount: Optional[float] = None
    is_paid: bool

    class Config:
        from_attributes = True
