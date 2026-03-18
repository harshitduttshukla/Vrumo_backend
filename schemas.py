from pydantic import BaseModel,EmailStr,Field
from typing import Optional
from enum import Enum
from datetime import datetime


class UserRole(str,Enum):
    customer = "customer"
    admin = "admin"


class UserCreate(BaseModel):
    name : str = Field(...,min_length=3,max_length=50)
    email : EmailStr
    phone : str = Field(...,min_length=10,max_length=15)
    password : str = Field(...,min_length=8,max_length=50)
    role : UserRole = Field(default=UserRole.customer)


class UserResponse(BaseModel):
    id : str
    name : str
    email : EmailStr
    phone : str
    role : UserRole
    created_at : datetime

    class Config:
        from_attributes = True


class ServiceCategory(str,Enum):
    car = "car"
    bike = "bike"

class ServiceCreate(BaseModel):
    name :str = Field(...,min_length=3,max_length=255)
    description : Optional[str] = None
    price : float = Field(...,gt=0)
    image_url : Optional[str] = None
    category : ServiceCategory = Field(...)
    is_active:Optional[bool] = True


class ServiceResponse(BaseModel):
    id : str
    name : str
    description : Optional[str] 
    price : float
    image_url : Optional[str]
    category : ServiceCategory
    is_active : bool
    created_at : datetime

    class Config: 
        from_attributes = True