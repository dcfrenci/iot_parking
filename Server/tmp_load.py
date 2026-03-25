import datetime
from database import SessionLocal, engine, Base
from models import User, Plate, Parking, Booking, ParkingSession

# Creates the tables in the database if they do not already exist
Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()

    try:
        # Clear existing data to ensure a clean state
        db.query(ParkingSession).delete()
        db.query(Booking).delete()
        db.query(Plate).delete()
        db.query(Parking).delete()
        db.query(User).delete()

        # 1. Insert User
        # String IDs from the dummy dict are mapped to integer IDs to satisfy the model constraints.
        user = User(
            id=1,
            name="Mario Rossi",
            email="mario.rossi@example.com",
            password="dummy_password_123" # Included because the models require a password.
        )
        db.add(user)

        # 2. Insert Parkings
        p1 = Parking(
            id=1,
            name="Central Station Parking",
            address="Piazza Dante 1",
            latitude=44.6471,
            longitude=10.9252,
            available_slots=12,
            total_slots=50,
            price_per_hour=2.50
        )
        
        p2 = Parking(
            id=2,
            name="City Center Garage",
            address="Via Emilia Centro 100",
            latitude=44.6460,
            longitude=10.9255,
            available_slots=3,
            total_slots=20,
            price_per_hour=3.00
        )
        db.add_all([p1, p2])

        # 3. Insert Plates
        pl1 = Plate(
            id=1,
            name="My Car",
            plate_text="AB123CD",
            is_active=True,
            user_id=1
        )
        
        pl2 = Plate(
            id=2,
            name="Wife's Car",
            plate_text="XY987ZT",
            is_active=False,
            user_id=1
        )
        db.add_all([pl1, pl2])

        # 4. Insert Bookings
        b1 = Booking(
            name="Weekend trip",
            parking_id=2,
            parking_name="City Center Garage",
            price_per_hour=3.00,
            date=datetime.datetime(2026, 3, 20, 10, 0, 0),
            car_plate="AB123CD",
            slot_code="A12",
            days=2,
            user_id=1
        )
        
        b2 = Booking(
            name="Airport stay",
            parking_id=1,
            parking_name="Central Station Parking",
            price_per_hour=2.65,
            date=datetime.datetime(2026, 2, 15, 8, 0, 0),
            car_plate="XY987ZT",
            slot_code="C45",
            days=5,
            user_id=1
        )
        db.add_all([b1, b2])

        # 5. Insert Current Parking as an active ParkingSession
        # The 'current_parking' dummy state maps cleanly to an ongoing ParkingSession.
        current_session = ParkingSession(
            plate_id=1, 
            parking_id=1, 
            entry_time=datetime.datetime(2026, 3, 23, 18, 0, 0),
            is_paid=False
        )
        db.add(current_session)

        # Execute and save to sqlite
        db.commit()
        print("Database populated successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()