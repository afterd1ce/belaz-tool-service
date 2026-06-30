from fastapi import APIRouter, Depends, HTTPException, Query
from schemas.instrument import CreateInstrument, UpdateInstrument
from services.instrument_service import InstrumentService
from api.v1.dependencies import get_instrument_service
from core.deps import require_role
from models.user import UserRole

router = APIRouter()


@router.get("/api/v1/instruments")
def list_instruments(
    workshop: str | None = Query(None),
    status: str | None = Query(None),
    type: str | None = Query(None),
    instrument_service: InstrumentService = Depends(get_instrument_service),
):
    return instrument_service.get_all(workshop, status, type)


@router.post("/api/v1/instruments")
def create_instrument(
    data: CreateInstrument,
    instrument_service: InstrumentService = Depends(get_instrument_service),
    _=Depends(require_role(UserRole.ADMIN, UserRole.METROLOGIST)),
):
    return instrument_service.create(data)


@router.get("/api/v1/instruments/{inst_id}")
def get_instrument(inst_id: str, instrument_service: InstrumentService = Depends(get_instrument_service)):
    try:
        return instrument_service.get_by_id(inst_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/api/v1/instruments/{inst_id}")
def update_instrument(
    inst_id: str,
    data: UpdateInstrument,
    instrument_service: InstrumentService = Depends(get_instrument_service),
    _=Depends(require_role(UserRole.ADMIN, UserRole.METROLOGIST)),
):
    try:
        return instrument_service.update(inst_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/api/v1/instruments/{inst_id}")
def delete_instrument(
    inst_id: str,
    instrument_service: InstrumentService = Depends(get_instrument_service),
    _=Depends(require_role(UserRole.ADMIN)),
):
    try:
        return instrument_service.delete(inst_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))