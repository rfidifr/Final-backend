from fastapi import FastAPI, Depends, HTTPException, status
from app.routers import admin, manager,login
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