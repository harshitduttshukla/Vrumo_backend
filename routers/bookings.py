from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from database_models import Booking, Service
from schemas import BookingCreate, BookingResponse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Create Booking
@router.post("/", response_model=BookingResponse)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == data.service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    new_booking = Booking(
        user_id=data.user_id,
        service_id=data.service_id,
        vehicle_type=data.vehicle_type,
        vehicle_model=data.vehicle_model,
        address=data.address,
        booking_date=data.booking_date,
        time_slot=data.time_slot,
        total_price=service.price,  # lock price
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