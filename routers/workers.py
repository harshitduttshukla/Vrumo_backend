from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from database_models import User, UserRole
from schemas import UserResponse
from app.utils.geo import haversine_distance
from typing import List

router = APIRouter()

# get_db moved to database.py

@router.get("/nearby", response_model=List[UserResponse])
def get_nearby_workers(
    lat: float, 
    lng: float, 
    radius_km: float = 5.0, 
    db: Session = Depends(get_db)
):
    # 1. Fetch all users with 'worker' role
    workers = db.query(User).filter(User.role == UserRole.worker).all()
    
    # 2. Filter by distance using Haversine formula
    nearby = []
    for worker in workers:
        if worker.latitude is not None and worker.longitude is not None:
            dist = haversine_distance(lat, lng, worker.latitude, worker.longitude)
            if dist <= radius_km:
                worker.distance = dist # Optional: add distance to response if schema allows
                nearby.append(worker)
    
    # 3. Sort by distance
    nearby.sort(key=lambda x: getattr(x, "distance", 999999))
    
    return nearby
