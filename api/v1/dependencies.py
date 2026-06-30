from sqlalchemy.orm import Session
from fastapi import Depends
from db.database import get_db
from services.auth_service import AuthService
from services.instrument_service import InstrumentService
from services.movement_service import MovementService
from services.calibration_service import CalibrationService


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_instrument_service(db: Session = Depends(get_db)) -> InstrumentService:
    return InstrumentService(db)


def get_movement_service(db: Session = Depends(get_db)) -> MovementService:
    return MovementService(db)


def get_calibration_service(db: Session = Depends(get_db)) -> CalibrationService:
    return CalibrationService(db)