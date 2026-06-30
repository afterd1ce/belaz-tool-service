from fastapi import APIRouter, Depends, HTTPException
from schemas.movement import IssueInstrument, ReturnInstrument
from services.movement_service import MovementService
from api.v1.dependencies import get_movement_service
from core.deps import require_role
from models.user import UserRole

router = APIRouter(prefix="/api/v1/movements", tags=["movements"])


@router.post("/issue")
def issue(
    data: IssueInstrument,
    movement_service: MovementService = Depends(get_movement_service),
    _=Depends(require_role(UserRole.ADMIN, UserRole.METROLOGIST)),
):
    try:
        return movement_service.issue(data.instrument_barcode, data.worker_badge_number)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/return")
def return_instrument(
    data: ReturnInstrument,
    movement_service: MovementService = Depends(get_movement_service),
    _=Depends(require_role(UserRole.ADMIN, UserRole.METROLOGIST)),
):
    try:
        return movement_service.return_instrument(data.instrument_barcode, data.condition_ok, data.notes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{inst_id}")
def history(inst_id: str, movement_service: MovementService = Depends(get_movement_service)):
    return movement_service.get_history(inst_id)