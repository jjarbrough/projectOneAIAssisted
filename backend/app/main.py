from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, lists, tasks
from app.api import deps
from app.core.config import Settings, get_settings
from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.session import create_engine_from_settings, create_session_factory
from app.services.notifier import TaskNotifier


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(title=app_settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    engine = create_engine_from_settings(app_settings)
    session_factory = create_session_factory(engine)
    deps.set_session_factory(session_factory)
    Base.metadata.create_all(bind=engine)

    app.state.settings = app_settings
    app.state.task_notifier = TaskNotifier()

    app.include_router(auth.router)
    app.include_router(lists.router)
    app.include_router(tasks.router)

    return app


app = create_app()

