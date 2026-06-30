from datetime import datetime
from sqlalchemy.orm import Session
from models.instrument import Instrument, InstrumentStatus
from models.user import User
from models.movement import Movement
from services.interfaces import IMovementService


def _mov_to_dict(mov: Movement) -> dict:
    return {
        "id": str(mov.id),
        "instrument_id": str(mov.instrument_id),
        "user_id": str(mov.user_id),
        "action": mov.action,
        "issued_at": str(mov.issued_at) if mov.issued_at else None,
        "returned_at": str(mov.returned_at) if mov.returned_at else None,
        "condition_ok": mov.condition_ok,
        "notes": mov.notes,
    }


class MovementService(IMovementService):
    def __init__(self, db: Session):
        self.db = db

    def issue(self, barcode: str, worker_badge: str) -> dict:
        inst = self.db.query(Instrument).filter(Instrument.barcode == barcode).first()
        if not inst:
            raise ValueError("Instrument not found")
        if inst.status == InstrumentStatus.EXPIRED:
            raise ValueError("Verification expired, cannot issue")
        if inst.status == InstrumentStatus.WRITTEN_OFF:
            raise ValueError("Instrument is written off")
        if inst.status != InstrumentStatus.AVAILABLE:
            raise ValueError(f"Instrument not available, status: {inst.status.value}")
        if inst.next_verification_date and inst.next_verification_date <= datetime.utcnow():
            inst.status = InstrumentStatus.EXPIRED
            self.db.commit()
            raise ValueError("Verification period has expired")
        worker = self.db.query(User).filter(User.badge_number == worker_badge).first()
        if not worker:
            raise ValueError("Worker not found")
        inst.status = InstrumentStatus.IN_USE
        movement = Movement(instrument_id=inst.id, user_id=worker.id, action="issue")
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)
        return _mov_to_dict(movement)

    def return_instrument(self, barcode: str, condition_ok: bool, notes: str | None) -> dict:
        inst = self.db.query(Instrument).filter(Instrument.barcode == barcode).first()
        if not inst:
            raise ValueError("Instrument not found")
        if inst.status != InstrumentStatus.IN_USE:
            raise ValueError("Instrument is not in use")
        movement = self.db.query(Movement).filter(Movement.instrument_id == inst.id, Movement.action == "issue").order_by(Movement.issued_at.desc()).first()
        if not movement:
            raise ValueError("Issue record not found")
        if not condition_ok:
            inst.status = InstrumentStatus.CALIBRATION_REQUIRED
        elif inst.next_verification_date and inst.next_verification_date <= datetime.utcnow():
            inst.status = InstrumentStatus.CALIBRATION_REQUIRED
        else:
            inst.status = InstrumentStatus.AVAILABLE
        movement.returned_at = datetime.utcnow()
        movement.condition_ok = condition_ok
        movement.notes = notes
        movement.action = "return"
        self.db.commit()
        self.db.refresh(movement)
        return _mov_to_dict(movement)

    def get_history(self, inst_id: str) -> list[dict]:
        movements = self.db.query(Movement).filter(Movement.instrument_id == inst_id).order_by(Movement.issued_at.desc()).all()
        return [_mov_to_dict(m) for m in movements]