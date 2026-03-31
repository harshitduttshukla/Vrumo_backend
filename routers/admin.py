from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal, get_db
from database_models import User, Booking, Service, BookingStatus
from schemas import UserResponse, BookingResponse, ServiceResponse
from typing import List, Dict, Any

router = APIRouter()

# get_db moved to database.py

@router.get("/stats", response_model=Dict[str, Any])
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_bookings = db.query(Booking).count()
    total_services = db.query(Service).count()
    
    # Calculate total revenue from completed bookings
    total_revenue = db.query(func.sum(Booking.total_price)).filter(Booking.status == BookingStatus.completed).scalar() or 0.0
    
    # Bookings by status
    status_counts = db.query(Booking.status, func.count(Booking.id)).group_by(Booking.status).all()
    bookings_by_status = {status.value: count for status, count in status_counts}
    
    return {
        "total_users": total_users,
        "total_bookings": total_bookings,
        "total_services": total_services,
        "total_revenue": total_revenue,
        "bookings_by_status": bookings_by_status
    }

@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/bookings", response_model=List[BookingResponse])
def get_all_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).order_by(Booking.created_at.desc()).all()

@router.put("/bookings/{booking_id}/status")
def update_booking_status(booking_id: str, status: BookingStatus, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = status
    db.commit()
    return {"message": f"Booking status updated to {status}"}

@router.delete("/bookings/{booking_id}")
def delete_booking(booking_id: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.delete(booking)
    db.commit()
    return {"message": "Booking deleted successfully"}
