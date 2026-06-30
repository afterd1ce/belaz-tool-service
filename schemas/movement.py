from pydantic import BaseModel


class IssueInstrument(BaseModel):
    instrument_barcode: str
    worker_badge_number: str


class ReturnInstrument(BaseModel):
    instrument_barcode: str
    condition_ok: bool = True
    notes: str | None = None