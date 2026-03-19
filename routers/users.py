from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from database_models import User
from schemas import UserCreate, UserResponse
from utils import hash_password


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        return existing_user

    # Check if phone exists
    existing_phone = db.query(User).filter(User.phone == user.phone).first()
    if existing_phone:
        return existing_phone

    hashed_password = hash_password(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password_hash=hashed_password,
        role=user.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/",response_model=list[UserResponse])
def get_user(user_id:str,db:Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
