import uuid
from sqlalchemy.orm import Session
from models.instrument import Instrument, InstrumentStatus
from services.interfaces import IInstrumentService


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


class InstrumentService(IInstrumentService):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, workshop=None, status=None, type=None) -> list[dict]:
        query = self.db.query(Instrument)
        if workshop:
            query = query.filter(Instrument.workshop == workshop)
        if status:
            query = query.filter(Instrument.status == status)
        if type:
            query = query.filter(Instrument.model.ilike(f"%{type}%"))
        return [_to_dict(r) for r in query.all()]

    def create(self, data) -> dict:
        barcode = f"BELAZ-{uuid.uuid4().hex[:8].upper()}"
        inst = Instrument(barcode=barcode, name=data.name, model=data.model, serial_number=data.serial_number, workshop=data.workshop)
        self.db.add(inst)
        self.db.commit()
        self.db.refresh(inst)
        return _to_dict(inst)

    def get_by_id(self, inst_id: str) -> dict:
        inst = self.db.query(Instrument).filter(Instrument.id == inst_id).first()
        if not inst:
            raise ValueError("Instrument not found")
        return _to_dict(inst)

    def update(self, inst_id: str, data) -> dict:
        inst = self.db.query(Instrument).filter(Instrument.id == inst_id).first()
        if not inst:
            raise ValueError("Instrument not found")
        if data.name is not None:
            inst.name = data.name
        if data.workshop is not None:
            inst.workshop = data.workshop
        if data.next_verification_date is not None:
            from datetime import datetime
            inst.next_verification_date = datetime.fromisoformat(data.next_verification_date)
        self.db.commit()
        self.db.refresh(inst)
        return _to_dict(inst)

    def delete(self, inst_id: str) -> dict:
        inst = self.db.query(Instrument).filter(Instrument.id == inst_id).first()
        if not inst:
            raise ValueError("Instrument not found")
        inst.status = InstrumentStatus.WRITTEN_OFF
        self.db.commit()
        return {"message": "Instrument written off", "status": "written_off"}