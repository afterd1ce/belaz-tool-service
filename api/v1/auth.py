from fastapi import APIRouter, Depends, HTTPException
from schemas.auth import LoginRequest, RefreshRequest
from services.auth_service import AuthService
from api.v1.dependencies import get_auth_service
from core.deps import get_current_user
from models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
def login(data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        return auth_service.login(data.badge_number, data.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/refresh")
def refresh(data: RefreshRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        return auth_service.refresh_token(data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me")
def profile(user: User = Depends(get_current_user), auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.get_profile(str(user.id))