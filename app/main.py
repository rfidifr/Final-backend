from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session 
from sqlalchemy import text        
from app.database import get_db
from app.routers import admin, manager, login
from app.database import Base,engine
from app import models

app = FastAPI(
    title="Secure RFID Arcade Management System",
    description="A multi-tenant system for managing arcade branches, managers, and RFID cards.",
)

app.include_router(admin.router)
app.include_router(manager.router)
app.include_router(login.router)

@app.get("/")
def home():
    return {"message": "go to /docs"}

#HEALTH CHECKPOINT FOR SEEING IF THE DATABASE IS CONNECTED PROPERLY.
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
    
        db.execute(text("SELECT 1"))
        return {
            "status": "online",
            "database": "connected",
            "message": "FastAPI is talking to Render PostgreSQL!"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database connection failed: {str(e)}"
        )
#Creating the tables in the databse if they dont exist
try:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
except Exception as e:
    print(f"Error creating tables: {e}")

