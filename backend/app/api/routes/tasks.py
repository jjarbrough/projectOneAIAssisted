from __future__ import annotations

import anyio
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import get_settings
from app.db import models
from app.schemas.task import TaskCreate, TaskRead, TaskReorderRequest, TaskUpdate
from app.services.notifier import TaskNotifier
from app.services.task import TaskService

router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/lists/{list_id}/tasks", response_model=list[TaskRead])
def list_tasks(
    list_id: int,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> list[TaskRead]:
    service = TaskService(db)
    return service.list_tasks(list_id=list_id, owner_id=current_user.id)


@router.post("/lists/{list_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    list_id: int,
    payload: TaskCreate,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
    notifier: TaskNotifier = Depends(deps.get_task_notifier),
) -> TaskRead:
    service = TaskService(db)
    task = service.create_task(
        list_id=list_id,
        owner_id=current_user.id,
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date,
        status=payload.status.value,
        priority=payload.priority.value,
        tags=payload.tags,
    )
    _notify_task_change(notifier, list_id)
    return task


@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
    notifier: TaskNotifier = Depends(deps.get_task_notifier),
) -> TaskRead:
    service = TaskService(db)
    task = service.update_task(
        task_id=task_id,
        owner_id=current_user.id,
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date,
        status=payload.status.value if payload.status else None,
        priority=payload.priority.value if payload.priority else None,
        tags=payload.tags,
    )
    _notify_task_change(notifier, task.list_id)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
    notifier: TaskNotifier = Depends(deps.get_task_notifier),
) -> None:
    service = TaskService(db)
    list_id = service.delete_task(task_id=task_id, owner_id=current_user.id)
    _notify_task_change(notifier, list_id)


@router.put("/lists/{list_id}/tasks/reorder", response_model=list[TaskRead])
def reorder_tasks(
    list_id: int,
    payload: TaskReorderRequest,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
    notifier: TaskNotifier = Depends(deps.get_task_notifier),
) -> list[TaskRead]:
    task_ids = payload.task_ids
    if not task_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="task_ids cannot be empty")
    service = TaskService(db)
    updated_tasks = service.reorder_tasks(list_id=list_id, owner_id=current_user.id, ordered_ids=task_ids)
    _notify_task_change(notifier, list_id)
    return updated_tasks


@router.websocket("/ws/lists/{list_id}")
async def task_updates_websocket(
    websocket: WebSocket,
    list_id: int,
    token: str,
    db: Session = Depends(deps.get_db),
) -> None:
    settings = get_settings()
    try:
        user = deps.get_user_from_token(token=token, db=db, settings=settings)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    service = TaskService(db)
    try:
        service.list_tasks(list_id=list_id, owner_id=user.id)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    notifier: TaskNotifier = websocket.app.state.task_notifier  # type: ignore[attr-defined]
    await notifier.connect(list_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await notifier.disconnect(list_id, websocket)


def _notify_task_change(notifier: TaskNotifier, list_id: int) -> None:
    message = {"type": "tasks_changed", "list_id": list_id}
    anyio.from_thread.run(notifier.broadcast, list_id, message)

