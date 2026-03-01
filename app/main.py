from email.mime import text

from fastapi import FastAPI, Depends, HTTPException, status
from requests import Session
from app.database import get_db
from app.routers  import admin, manager,login
app=FastAPI(
    title="Secure RFID Arcade Management System",
    description="A multi-tenant system for managing arcade branches, managers, and RFID cards.",
)

app.include_router(admin.router)
app.include_router(manager.router)
app.include_router(login.router)

@app.get("/")
def home():
    return {"message":"go to /docs"}

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
        # This will catch connection timeouts or credential errors
        raise HTTPException(
            status_code=500, 
            detail=f"Database connection failed: {str(e)}")    