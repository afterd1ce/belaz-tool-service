from sqlalchemy.orm import Session
from models.user import User
from core.security import verify_password, create_access_token, create_refresh_token, decode_token
from services.interfaces import IAuthService


class AuthService(IAuthService):
    def __init__(self, db: Session):
        self.db = db

    def login(self, badge_number: str, password: str) -> dict:
        user = self.db.query(User).filter(User.badge_number == badge_number).first()
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid badge number or password")
        return {
            "access_token": create_access_token(str(user.id), user.role.value),
            "refresh_token": create_refresh_token(str(user.id)),
            "token_type": "bearer"
        }

    def refresh_token(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        user = self.db.query(User).filter(User.id == payload.get("sub")).first()
        if not user:
            raise ValueError("User not found")
        return {
            "access_token": create_access_token(str(user.id), user.role.value),
            "refresh_token": create_refresh_token(str(user.id)),
            "token_type": "bearer"
        }

    def get_profile(self, user_id: str) -> dict:
        user = self.db.query(User).filter(User.id == user_id).first()
        return {
            "id": str(user.id),
            "badge_number": user.badge_number,
            "full_name": user.full_name,
            "workshop": user.workshop,
            "role": user.role.value
        }