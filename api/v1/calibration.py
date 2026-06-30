from fastapi import APIRouter, Depends, HTTPException
from schemas.calibration import VerifyCalibration
from services.calibration_service import CalibrationService
from api.v1.dependencies import get_calibration_service
from core.deps import require_role
from models.user import UserRole

router = APIRouter(prefix="/api/v1/calibration", tags=["calibration"])


@router.get("/expired")
def expired(
    calibration_service: CalibrationService = Depends(get_calibration_service),
    _=Depends(require_role(UserRole.METROLOGIST, UserRole.ADMIN)),
):
    return calibration_service.get_expired()


@router.post("/verify")
def verify(
    data: VerifyCalibration,
    calibration_service: CalibrationService = Depends(get_calibration_service),
    _=Depends(require_role(UserRole.METROLOGIST, UserRole.ADMIN)),
):
    try:
        return calibration_service.verify(data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/daily-check")
def daily_check(calibration_service: CalibrationService = Depends(get_calibration_service)):
    return calibration_service.daily_check()