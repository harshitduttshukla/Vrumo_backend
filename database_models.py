import uuid
import enum
from sqlalchemy import Column, String, Enum, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()



class UserRole(str, enum.Enum):
    customer = "customer"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.customer)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)


class ServiceCategory(Base):
    car = "car"
    bike = "bike"


class Service(Base):
    __tablename__ = "services"

    id = Column(String(36), primary_key=True, default=lambda:str(uuid.uuid4()))
    name = Column(String(255),nullable=False)
    description = Column(String(255),nullable=False)
    price = Column()
    image_url = Column(DECIMAL(Text,nullable=False))
    category = Column(Enum(ServiceCategory),nullable=False)
    created_at = Column(TIMESTAMP,server_default=func.current_timestamp(),nullable=False)

    