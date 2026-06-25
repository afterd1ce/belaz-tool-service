import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import enum


class UserRole(str, enum.Enum):
    АДМИНИСТРАТОР = "администратор"
    МЕТРОЛОГ = "метролог"
    РАБОЧИЙ = "рабочий"


class InstrumentStatus(str, enum.Enum):
    ДОСТУПЕН = "доступен"
    В_РАБОТЕ = "в_работе"
    ТРЕБУЕТСЯ_ПОВЕРКА = "требуется_поверка"
    ПРОСРОЧЕН = "просрочен"
    СПИСАН = "списан"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    badge_number = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    workshop = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.РАБОЧИЙ)
    hashed_password = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    barcode = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    serial_number = Column(String(100), nullable=False)
    workshop = Column(String(50), nullable=False)
    status = Column(Enum(InstrumentStatus), default=InstrumentStatus.ДОСТУПЕН)
    last_verification_date = Column(DateTime, nullable=True)
    next_verification_date = Column(DateTime, nullable=True)
    certificate_number = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Movement(Base):
    __tablename__ = "movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey("instruments.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(20), nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    returned_at = Column(DateTime, nullable=True)
    condition_ok = Column(Boolean, nullable=True)
    notes = Column(String(255), nullable=True)


class Calibration(Base):
    __tablename__ = "calibrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey("instruments.id"), nullable=False)
    verification_date = Column(DateTime, nullable=False)
    next_verification_date = Column(DateTime, nullable=False)
    certificate_number = Column(String(100), nullable=False)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)