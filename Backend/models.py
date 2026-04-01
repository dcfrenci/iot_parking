from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    account_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Preferences
    pref_distance = Column(Float, default=2.5)
    pref_price = Column(Float, default=5.0)

    # Relationships
    plates = relationship("Plate", back_populates="owner", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="owner", uselist=False, cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="owner", cascade="all, delete-orphan")

class Plate(Base):
    __tablename__ = "plates"
    
    plate_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("users.account_id"))
    plate_text = Column(String, index=True)
    plate_name = Column(String)
    is_active = Column(Boolean, default=True)
    image_uri = Column(String, nullable=True)

    owner = relationship("User", back_populates="plates")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("users.account_id"), unique=True)
    circuit = Column(String)
    card_number = Column(String)

    owner = relationship("User", back_populates="payment")

class Parking(Base):
    __tablename__ = "parkings"
    
    parking_id = Column(Integer, primary_key=True, index=True)
    parking_name = Column(String, index=True)
    total_slot = Column(Integer)
    available_slot = Column(Integer)
    price_per_hour = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
    address = Column(String)

class Parked(Base):
    __tablename__ = "parked_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    plate_id = Column(Integer, ForeignKey("plates.plate_id"))
    parking_id = Column(Integer, ForeignKey("parkings.parking_id"))
    entry_time = Column(DateTime)
    amount = Column(Float, default=0.0)
    is_paid = Column(Boolean, default=False)

class Booking(Base):
    __tablename__ = "bookings"
    
    booking_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("users.account_id"))
    parking_id = Column(Integer, ForeignKey("parkings.parking_id"))
    plate_id = Column(Integer, ForeignKey("plates.plate_id"))
    booking_name = Column(String)
    date = Column(Date)
    days = Column(Integer)
    slot_code = Column(Integer)

    parking = relationship("Parking") 
    plate = relationship("Plate")

    owner = relationship("User", back_populates="bookings")