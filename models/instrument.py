import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from db.database import Base
import enum


class InstrumentStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    CALIBRATION_REQUIRED = "calibration_required"
    EXPIRED = "expired"
    WRITTEN_OFF = "written_off"


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    barcode = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    serial_number = Column(String(100), nullable=False)
    workshop = Column(String(50), nullable=False)
    status = Column(Enum(InstrumentStatus), default=InstrumentStatus.AVAILABLE)
    last_verification_date = Column(DateTime, nullable=True)
    next_verification_date = Column(DateTime, nullable=True)
    certificate_number = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)