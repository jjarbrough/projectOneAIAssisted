from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user import UserRepository


class AuthService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings
        self.users = UserRepository(session)

    def register_user(self, *, email: str, password: str, full_name: str | None = None):
        existing = self.users.get_by_email(email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        hashed = hash_password(password)
        user = self.users.create(email=email, hashed_password=hashed, full_name=full_name)
        token = self._token_for_user(user.id)
        return user, token

    def authenticate(self, *, email: str, password: str):
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = self._token_for_user(user.id)
        return user, token

    def _token_for_user(self, user_id: int) -> str:
        return create_access_token(
            subject=str(user_id),
            secret_key=self.settings.secret_key,
            algorithm=self.settings.algorithm,
            expires_minutes=self.settings.access_token_expire_minutes,
        )

