from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models
from app.schemas.task import TaskListCreate, TaskListRead
from app.services.task import TaskService

router = APIRouter(prefix="/api", tags=["task-lists"])


@router.get("/lists", response_model=list[TaskListRead])
def get_lists(
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> list[TaskListRead]:
    service = TaskService(db)
    return service.list_lists(owner_id=current_user.id)


@router.post("/lists", response_model=TaskListRead, status_code=status.HTTP_201_CREATED)
def create_list(
    payload: TaskListCreate,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> TaskListRead:
    service = TaskService(db)
    return service.create_list(owner_id=current_user.id, name=payload.name)

