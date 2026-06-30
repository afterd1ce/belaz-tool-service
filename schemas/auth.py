from pydantic import BaseModel


class LoginRequest(BaseModel):
    badge_number: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str