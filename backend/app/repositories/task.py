from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import models


class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        list_id: int,
        title: str,
        description: str | None,
        due_date,
        status: str,
        priority: str,
        tags: list[str],
    ) -> models.Task:
        next_position = self._next_position(list_id)
        task = models.Task(
            list_id=list_id,
            title=title,
            description=description,
            due_date=due_date,
            status=status,
            priority=priority,
            tags=tags,
            position=next_position,
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_by_id(self, task_id: int) -> models.Task | None:
        return self.session.query(models.Task).filter(models.Task.id == task_id).first()

    def list_for_task_list(self, list_id: int) -> list[models.Task]:
        return (
            self.session.query(models.Task)
            .filter(models.Task.list_id == list_id)
            .order_by(models.Task.position.asc(), models.Task.created_at.asc())
            .all()
        )

    def delete(self, task: models.Task) -> None:
        list_id = task.list_id
        self.session.delete(task)
        self.session.commit()
        self._resequence_positions(list_id)

    def update(
        self,
        task: models.Task,
        *,
        title: str | None = None,
        description: str | None = None,
        due_date=None,
        status: str | None = None,
        priority: str | None = None,
        tags: list[str] | None = None,
    ) -> models.Task:
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if due_date is not None:
            task.due_date = due_date
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority
        if tags is not None:
            task.tags = tags
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def reorder(self, list_id: int, ordered_ids: list[int]) -> list[models.Task]:
        tasks = self.list_for_task_list(list_id)
        task_by_id = {task.id: task for task in tasks}
        if set(task_by_id.keys()) != set(ordered_ids):
            raise ValueError("Provided task IDs do not match tasks in list")

        for position, task_id in enumerate(ordered_ids):
            task = task_by_id[task_id]
            task.position = position
            self.session.add(task)
        self.session.commit()
        return self.list_for_task_list(list_id)

    def _next_position(self, list_id: int) -> int:
        max_position = (
            self.session.query(func.max(models.Task.position))
            .filter(models.Task.list_id == list_id)
            .scalar()
        )
        if max_position is None:
            return 0
        return max_position + 1

    def _resequence_positions(self, list_id: int) -> None:
        tasks = self.list_for_task_list(list_id)
        for position, task in enumerate(tasks):
            if task.position != position:
                task.position = position
                self.session.add(task)
        self.session.commit()

