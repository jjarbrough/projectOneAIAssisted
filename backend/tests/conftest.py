from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.core.config import Settings
from app.db.base import Base
from app.main import create_app


@pytest.fixture()
def settings(tmp_path_factory: pytest.TempPathFactory) -> Settings:
    db_path = tmp_path_factory.mktemp("db") / "test.db"
    return Settings(
        app_name="TaskTrack-Test",
        database_url=f"sqlite:///{db_path}",
        secret_key="test-secret-key",
        access_token_expire_minutes=30,
    )


@pytest.fixture()
def engine(settings: Settings):
    engine = create_engine(
        settings.database_url, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def session_factory(engine) -> sessionmaker:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def client(settings: Settings, session_factory: sessionmaker) -> Generator[TestClient, None, None]:
    app = create_app(settings=settings)

    def _get_test_db() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _get_test_db

    with TestClient(app) as test_client:
        yield test_client

