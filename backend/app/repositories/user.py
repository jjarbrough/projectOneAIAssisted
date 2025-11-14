from __future__ import annotations

from sqlalchemy.orm import Session

from app.db import models


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> models.User | None:
        return self.session.query(models.User).filter(models.User.email == email).first()

    def get_by_id(self, user_id: int) -> models.User | None:
        return self.session.query(models.User).filter(models.User.id == user_id).first()

    def create(self, email: str, hashed_password: str, full_name: str | None = None) -> models.User:
        user = models.User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

