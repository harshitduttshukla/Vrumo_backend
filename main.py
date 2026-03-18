from fastapi import FastAPI
from database import engine
from database_models import Base

from routers import users,services

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vrumo API",
    description="Backend for Vrumo Car and Bike Servies",
    version="0.0.1"
)

@app.get("/")
def root():
    return {"message": "🚀 Vrumo API is running"}

#Include routers
app.include_router(users.router,prefix="/users",tags=["Users"])
app.include_router(services.router,prefix="/services",tags=["Services"])

