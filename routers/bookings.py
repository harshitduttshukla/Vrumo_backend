from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import Union
from utils import hash_password
from database_models import Booking, Service, User, UserRole
from schemas import BookingCreate, BookingResponse, BookingFlatCreate

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Create Booking (Supports both standard and flat payloads)
@router.post("/", response_model=BookingResponse)
def create_booking(data: Union[BookingCreate, BookingFlatCreate], db: Session = Depends(get_db)):
    if hasattr(data, "email"):  # Check if it's BookingFlatCreate
        # 1. Find or Create User (Check both email and phone to avoid UniqueViolation)
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            # Check if phone already exists for a different email
            user = db.query(User).filter(User.phone == data.phone).first()
            
        if not user:
            user = User(
                name=data.name,
                email=data.email,
                phone=data.phone,
                password_hash=hash_password("vrumopassword"),
                role=UserRole.customer
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # If user exists (by email or phone), optionally update the name if it's missing or different
            if not user.name and data.name:
                user.name = data.name
                db.commit()

        # 2. Find Service (Case-insensitive match on name)
        service = db.query(Service).filter(Service.name.ilike(f"%{data.serviceType}%")).first()
        if not service:
            # Fallback to first available service if not found, or raise error
            service = db.query(Service).first()
            if not service:
                raise HTTPException(status_code=404, detail="No services available in database")

        user_id = user.id
        service_id = service.id
        vehicle_type = data.vehicleType
        vehicle_model = "Not Specified" # Default since not in flat schema
        address = data.address
        booking_date = data.date
        time_slot = data.time
        total_price = service.price
    else:
        # Standard BookingCreate logic
        service = db.query(Service).filter(Service.id == data.service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        user_id = data.user_id
        service_id = data.service_id
        vehicle_type = data.vehicle_type
        vehicle_model = data.vehicle_model
        address = data.address
        booking_date = data.booking_date
        time_slot = data.time_slot
        total_price = service.price

    new_booking = Booking(
        user_id=user_id,
        service_id=service_id,
        vehicle_type=vehicle_type,
        vehicle_model=vehicle_model,
        address=address,
        booking_date=booking_date,
        time_slot=time_slot,
        total_price=total_price,
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking


# ✅ Get all bookings
@router.get("/", response_model=list[BookingResponse])
def get_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()


# ✅ Get bookings by user
@router.get("/user/{user_id}", response_model=list[BookingResponse])
def get_user_bookings(user_id: str, db: Session = Depends(get_db)):
    return db.query(Booking).filter(Booking.user_id == user_id).all()


# ✅ Update status (admin use)
@router.put("/{booking_id}/status")
def update_status(booking_id: str, status: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = status
    db.commit()

    return {"message": "Status updated"}