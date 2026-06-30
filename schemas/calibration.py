from pydantic import BaseModel


class VerifyCalibration(BaseModel):
    instrument_id: str
    verification_date: str
    next_verification_date: str
    certificate_number: str