from database import Base
from sqlalchemy import Column
from sqlalchemy import Integer, String, Boolean, DateTime, Float
from sqlalchemy import ForeignKey


class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True)
    name     = Column(String)
    email    = Column(String, unique=True)
    password = Column(String)


class Plate(Base):
    __tablename__ = "plates"

    id         = Column(Integer, primary_key=True)
    name       = Column(String)
    plate_text = Column(String, unique=True)
    is_active  = Column(Boolean, default=False)
    image_uri  = Column(String, nullable=True)
    user_id    = Column(Integer, ForeignKey("users.id"))


class Parking(Base):
    __tablename__ = "parkings"

    id               = Column(Integer, primary_key=True)
    name             = Column(String)
    address          = Column(String)
    latitude         = Column(Float)
    longitude        = Column(Float)
    available_slots  = Column(Integer)
    total_slots      = Column(Integer)
    price_per_hour   = Column(Float)


class Booking(Base):
    __tablename__ = "bookings"

    id             = Column(Integer, primary_key=True)
    name           = Column(String)
    parking_id     = Column(Integer, ForeignKey("parkings.id"))
    parking_name   = Column(String)
    date           = Column(DateTime)
    car_plate      = Column(String)
    slot_code      = Column(String)
    days           = Column(Integer)
    price_per_hour = Column(Float)
    user_id        = Column(Integer, ForeignKey("users.id"))


class ParkingSession(Base):
    __tablename__ = "sessions"

    id         = Column(Integer, primary_key=True)
    plate_id   = Column(Integer, ForeignKey("plates.id"))
    parking_id = Column(Integer, ForeignKey("parkings.id"))
    entry_time = Column(DateTime)
    exit_time  = Column(DateTime, nullable=True)
    amount     = Column(Float, nullable=True)
    is_paid    = Column(Boolean, default=False)
