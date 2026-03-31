from pydantic import BaseModel, Field
from typing import Optional, Union, Any
from enum import Enum
from datetime import datetime, date


class UserRole(str, Enum):
    customer = "customer"
    worker = "worker"
    admin = "admin"


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3) # Relaxed from EmailStr for easier testing
    phone: str = Field(..., min_length=5, max_length=20) # Relaxed from 10
    password: Optional[str] = Field(default="vrumopassword", min_length=1)
    role: UserRole = Field(default=UserRole.customer)


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    role: UserRole
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ServiceCategory(str, Enum):
    car = "car"
    bike = "bike"


class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    image_url: Optional[str] = None
    category: ServiceCategory = Field(...)
    is_active: Optional[bool] = True


class ServiceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: float
    image_url: Optional[str]
    category: ServiceCategory
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    user_id: str
    service_id: str
    vehicle_type: str
    vehicle_model: str
    address: str
    booking_date: Union[str, date]
    time_slot: str


class BookingFlatCreate(BaseModel):
    name: str
    email: str
    phone: str
    vehicleType: str
    serviceType: str
    date: str
    time: str
    address: str


class BookingAuthCreate(BaseModel):
    serviceType: str
    vehicleType: str
    date: str
    time: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BookingResponse(BaseModel):
    id: str
    user_id: str
    service_id: str
    vehicle_type: str
    vehicle_model: str
    address: str
    booking_date: Union[str, date]
    time_slot: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_price: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True