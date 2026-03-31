#all ready readed 
from pydantic import BaseModel, Field
from typing import Optional

class SendOTPRequest(BaseModel):
    phone_number: str = Field(..., pattern=r"^\d{10}$")

class VerifyOTPRequest(BaseModel):
    phone_number: str = Field(..., pattern=r"^\d{10}$")
    otp_code: str = Field(..., min_length=4, max_length=6)

class TokenResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    is_new_user: bool
    user: dict

class UpdateProfileRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=3)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
