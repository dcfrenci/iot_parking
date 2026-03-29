from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

DB_PATH = "sqlite:///./parking.db"

engine = create_engine(DB_PATH, echo=True)
SessionLocal = sessionmaker(engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
