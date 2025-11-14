from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import Settings, get_settings
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate
from app.services.auth import AuthService

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserCreate,
    db: Session = Depends(deps.get_db),
    settings: Settings = Depends(get_settings),
) -> Token:
    service = AuthService(db, settings)
    _, access_token = service.register_user(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
def login_user(
    payload: LoginRequest,
    db: Session = Depends(deps.get_db),
    settings: Settings = Depends(get_settings),
) -> Token:
    service = AuthService(db, settings)
    _, access_token = service.authenticate(
        email=payload.email,
        password=payload.password,
    )
    return Token(access_token=access_token)

