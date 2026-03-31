from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from typing import Union
from database_models import Booking, Service, User, UserRole, BookingStatus
from schemas import BookingCreate, BookingResponse, BookingFlatCreate, BookingAuthCreate
from app.modules.auth.auth_deps import get_current_user

router = APIRouter()


# get_db moved to database.py


# ✅ Create Booking (Authenticated)
@router.post("/", response_model=BookingResponse)
def create_booking(
    data: BookingAuthCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Find Service (Case-insensitive match on name)
    service = db.query(Service).filter(Service.name.ilike(f"%{data.serviceType}%")).first()
    if not service:
        # Fallback to first available service if not found
        service = db.query(Service).first()
        if not service:
            raise HTTPException(status_code=404, detail="No services available in database")

    # 2. Create the booking using current_user info
    new_booking = Booking(
        user_id=current_user.id,
        service_id=service.id,
        vehicle_type=data.vehicleType,
        vehicle_model="Not Specified",
        address=data.address,
        booking_date=data.date,
        time_slot=data.time,
        latitude=data.latitude,
        longitude=data.longitude,
        total_price=service.price,
        status=BookingStatus.pending
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking


# ✅ Get all bookings
@router.get("/", response_model=list[BookingResponse])
def get_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()


# ✅ Get bookings by user (Secured)
@router.get("/user/{user_id}", response_model=list[BookingResponse])
def get_user_bookings(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Security check: Ensure the requested user_id matches the logged-in token
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view these bookings")
    return db.query(Booking).filter(Booking.user_id == user_id).order_by(Booking.created_at.desc()).all()


# ✅ Update status (admin use)
@router.put("/{booking_id}/status")
def update_status(booking_id: str, status: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = status
    db.commit()

    return {"message": "Status updated"}