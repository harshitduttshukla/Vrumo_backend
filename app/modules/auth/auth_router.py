from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from app.modules.auth.auth_schema import SendOTPRequest, VerifyOTPRequest, TokenResponse, UpdateProfileRequest
from app.modules.auth.auth_service import auth_service
from app.modules.auth.auth_deps import get_current_user
from database_models import User

router = APIRouter()

# get_db moved to database.py

@router.post("/send-otp")
async def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    success, result = auth_service.generate_otp(request.phone_number, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=result
        )
    # result is a message string from service
    # We also return a hint for developers
    return {"message": "OTP sent successfully", "debug_otp": result if isinstance(result, str) and result.isdigit() else None}

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    try:
        success, message, data = auth_service.verify_otp(request.phone_number, request.otp_code, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        return {
            "message": message,
            "access_token": data["access_token"],
            "token_type": data["token_type"],
            "is_new_user": data["is_new_user"],
            "user": data["user"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone_number or current_user.phone,
        "role": current_user.role
    }

@router.put("/update-profile")
async def update_profile(
    request: UpdateProfileRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Check if email is already taken by another user
        existing_user = db.query(User).filter(User.email == request.email, User.id != current_user.id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        
        current_user.name = request.name
        current_user.email = request.email
        current_user.latitude = request.latitude
        current_user.longitude = request.longitude
        
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "id": str(current_user.id),
                "name": current_user.name,
                "email": current_user.email,
                "phone": current_user.phone_number or current_user.phone,
                "latitude": current_user.latitude,
                "longitude": current_user.longitude
            }
        }
    except Exception as e:
        db.rollback()
        print(f"❌ PROFILE UPDATE ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
