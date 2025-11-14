from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.core.security import decode_access_token
from app.repositories.user import UserRepository
from app.services.notifier import TaskNotifier

_SessionFactory: sessionmaker | None = None
_security = HTTPBearer(auto_error=False)


def set_session_factory(factory: sessionmaker) -> None:
    global _SessionFactory
    _SessionFactory = factory


def get_db() -> Generator[Session, None, None]:
    if _SessionFactory is None:
        raise RuntimeError("Database session factory is not configured.")
    session = _SessionFactory()
    try:
        yield session
    finally:
        session.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return _resolve_user_from_token(credentials.credentials, db, settings)


def get_user_from_token(
    token: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    return _resolve_user_from_token(token, db, settings)


def get_task_notifier(request: Request) -> TaskNotifier:
    notifier = getattr(request.app.state, "task_notifier", None)
    if notifier is None:
        raise RuntimeError("Task notifier not configured")
    return notifier


def _resolve_user_from_token(token: str, db: Session, settings: Settings):
    try:
        payload = decode_access_token(token, settings.secret_key, settings.algorithm)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        user_id = int(subject)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

