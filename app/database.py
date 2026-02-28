import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load the variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Render fix: SQLAlchemy requires 'postgresql://' instead of 'postgres://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This is our "Dependency" that routes will use to get a DB connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()