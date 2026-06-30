from pydantic import BaseModel


class CreateInstrument(BaseModel):
    name: str
    model: str
    serial_number: str
    workshop: str


class UpdateInstrument(BaseModel):
    name: str | None = None
    workshop: str | None = None
    next_verification_date: str | None = None