from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.instrument import Instrument, InstrumentStatus
from models.calibration import Calibration
from services.interfaces import ICalibrationService


def _to_dict(inst: Instrument) -> dict:
    return {
        "id": str(inst.id),
        "barcode": inst.barcode,
        "name": inst.name,
        "model": inst.model,
        "serial_number": inst.serial_number,
        "workshop": inst.workshop,
        "status": inst.status.value,
        "last_verification_date": str(inst.last_verification_date) if inst.last_verification_date else None,
        "next_verification_date": str(inst.next_verification_date) if inst.next_verification_date else None,
        "certificate_number": inst.certificate_number,
    }


class CalibrationService(ICalibrationService):
    def __init__(self, db: Session):
        self.db = db

    def get_expired(self) -> list[dict]:
        cutoff = datetime.utcnow() + timedelta(days=7)
        instruments = self.db.query(Instrument).filter(
            Instrument.next_verification_date <= cutoff,
            Instrument.status.in_(["available", "in_use", "expired"])
        ).all()
        return [_to_dict(i) for i in instruments]

    def verify(self, data) -> dict:
        inst = self.db.query(Instrument).filter(Instrument.id == data.instrument_id).first()
        if not inst:
            raise ValueError("Instrument not found")
        cal = Calibration(
            instrument_id=inst.id,
            verification_date=datetime.fromisoformat(data.verification_date),
            next_verification_date=datetime.fromisoformat(data.next_verification_date),
            certificate_number=data.certificate_number,
            performed_by=inst.id
        )
        inst.status = InstrumentStatus.AVAILABLE
        inst.last_verification_date = datetime.fromisoformat(data.verification_date)
        inst.next_verification_date = datetime.fromisoformat(data.next_verification_date)
        inst.certificate_number = data.certificate_number
        self.db.add(cal)
        self.db.commit()
        self.db.refresh(cal)
        return {
            "id": str(cal.id),
            "instrument_id": str(cal.instrument_id),
            "verification_date": str(cal.verification_date),
            "next_verification_date": str(cal.next_verification_date),
            "certificate_number": cal.certificate_number,
        }

    def daily_check(self) -> dict:
        now = datetime.utcnow()
        expired = self.db.query(Instrument).filter(
            Instrument.next_verification_date <= now,
            Instrument.status.in_([InstrumentStatus.AVAILABLE, InstrumentStatus.IN_USE])
        ).all()
        blocked = 0
        for inst in expired:
            inst.status = InstrumentStatus.EXPIRED
            blocked += 1
        self.db.commit()
        return {"status": "ok", "blocked_count": blocked, "checked_at": now.isoformat()}