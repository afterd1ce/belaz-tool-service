import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from db.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    METROLOGIST = "metrologist"
    WORKER = "worker"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    badge_number = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    workshop = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.WORKER)
    hashed_password = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)