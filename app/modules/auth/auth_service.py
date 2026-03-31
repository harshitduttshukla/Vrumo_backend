import random
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.orm import Session
from database_models import User, OTP
from app.services.sms_service import sms_service
import os

# JWT Settings
SECRET_KEY = os.getenv("JWT_SECRET", "vrumo_secret_key_123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

class AuthService:
    @staticmethod
    def generate_otp(phone_number: str, db: Session):
        # Rate limit check: max 3 OTP requests per minute
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_requests = db.query(OTP).filter(
            OTP.phone_number == phone_number,
            OTP.last_requested_at >= one_minute_ago
        ).count()
        
        if recent_requests >= 3:
            return False, "Too many OTP requests. Please wait a minute."

        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        # Store or Update OTP
        existing_otp = db.query(OTP).filter(OTP.phone_number == phone_number).first()
        if existing_otp:
            existing_otp.otp_code = otp_code
            existing_otp.expires_at = expires_at
            existing_otp.attempts = 0
            existing_otp.last_requested_at = datetime.utcnow()
        else:
            new_otp = OTP(
                phone_number=phone_number,
                otp_code=otp_code,
                expires_at=expires_at
            )
            db.add(new_otp)
        
        db.commit()
        
        # Send OTP
        sms_success = sms_service.send_otp(phone_number, otp_code)
        
        if not sms_success:
            return False, "Failed to send SMS. Please try again later."
            
        return True, otp_code

    @staticmethod
    def verify_otp(phone_number: str, otp_code: str, db: Session):
        otp_record = db.query(OTP).filter(OTP.phone_number == phone_number).first()
        
        if not otp_record:
            return False, "OTP not found", None

        # Check attempts
        if otp_record.attempts >= 5:
            return False, "Maximum attempts reached. Please request a new OTP.", None

        # Check expiry
        if otp_record.expires_at < datetime.utcnow():
            return False, "OTP expired. Please request a new one.", None

        # Check code
        if otp_record.otp_code != otp_code:
            otp_record.attempts += 1
            db.commit()
            return False, f"Invalid OTP. {5 - otp_record.attempts} attempts remaining.", None

        # OTP is valid - clear it
        db.delete(otp_record)
        db.commit() # Commit delete
        
        # Check if user exists (check both new and old columns)
        user = db.query(User).filter(
            (User.phone_number == phone_number) | (User.phone == phone_number)
        ).first()
        
        is_new_user = False
        if user:
            # Sync the new phone_number column if it's empty
            if not user.phone_number:
                user.phone_number = phone_number
                db.commit()
        else:
            is_new_user = True
            # Create a new user with default values
            # Using phone number as name initially
            # Ensure phone_number is long enough for slicing
            display_phone_suffix = phone_number[-4:] if len(phone_number) >= 4 else phone_number
            user_name = f"User {display_phone_suffix}"
            user = User(
                name=user_name,
                email=f"user_{phone_number}@vrumo.com",
                phone_number=phone_number,
                phone=phone_number, # Also populate old phone column for compatibility
                password_hash="OTP_USER", # dummy
                role="customer"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Generate JWT
        token_data = {"sub": user.id, "phone": user.phone_number}
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data.update({"exp": expire})
        
        access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        return True, "Login successful", {
            "access_token": access_token,
            "token_type": "bearer",
            "is_new_user": is_new_user,
            "user": {
                "id": user.id,
                "name": user.name,
                "phone": user.phone_number,
                "role": user.role
            }
        }

auth_service = AuthService()
