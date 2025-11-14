from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db import models
from app.repositories.task import TaskRepository
from app.repositories.task_list import TaskListRepository


class TaskService:
    def __init__(self, session: Session):
        self.session = session
        self.task_lists = TaskListRepository(session)
        self.tasks = TaskRepository(session)

    def create_list(self, *, owner_id: int, name: str) -> models.TaskList:
        return self.task_lists.create(owner_id=owner_id, name=name)

    def list_lists(self, *, owner_id: int) -> list[models.TaskList]:
        return self.task_lists.list_for_user(owner_id)

    def _require_list(self, list_id: int, owner_id: int) -> models.TaskList:
        task_list = self.task_lists.get_by_id(list_id)
        if task_list is None or task_list.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task list not found")
        return task_list

    def create_task(
        self,
        *,
        list_id: int,
        owner_id: int,
        title: str,
        description: str | None,
        due_date: date | None,
        status: str,
        priority: str,
        tags: list[str] | None,
    ) -> models.Task:
        self._require_list(list_id, owner_id)
        self._validate_status(status)
        validated_priority = self._validate_priority(priority)
        normalized_tags = self._normalize_tags(tags)
        return self.tasks.create(
            list_id=list_id,
            title=title,
            description=description,
            due_date=due_date,
            status=status,
            priority=validated_priority,
            tags=normalized_tags,
        )

    def list_tasks(self, *, list_id: int, owner_id: int) -> list[models.Task]:
        self._require_list(list_id, owner_id)
        return self.tasks.list_for_task_list(list_id)

    def update_task(
        self,
        *,
        task_id: int,
        owner_id: int,
        title: str | None,
        description: str | None,
        due_date: date | None,
        status: str | None,
        priority: str | None,
        tags: list[str] | None,
    ) -> models.Task:
        task = self.tasks.get_by_id(task_id)
        if task is None or task.task_list.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        if status is not None:
            self._validate_status(status)
        validated_priority = self._validate_priority(priority) if priority is not None else None
        normalized_tags = self._normalize_tags(tags) if tags is not None else None
        return self.tasks.update(
            task,
            title=title,
            description=description,
            due_date=due_date,
            status=status,
            priority=validated_priority,
            tags=normalized_tags,
        )

    def delete_task(self, *, task_id: int, owner_id: int) -> int:
        task = self.tasks.get_by_id(task_id)
        if task is None or task.task_list.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        list_id = task.list_id
        self.tasks.delete(task)
        return list_id

    def reorder_tasks(self, *, list_id: int, owner_id: int, ordered_ids: list[int]) -> list[models.Task]:
        self._require_list(list_id, owner_id)
        if not ordered_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task order cannot be empty",
            )
        try:
            return self.tasks.reorder(list_id, ordered_ids)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

    def _validate_status(self, status: str) -> None:
        if status not in {member.value for member in models.TaskStatusEnum}:
            valid = ", ".join(member.value for member in models.TaskStatusEnum)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Valid values: {valid}",
            )

    def _validate_priority(self, priority: str | None) -> str:
        value = priority or models.TaskPriorityEnum.medium.value
        if value not in {member.value for member in models.TaskPriorityEnum}:
            valid = ", ".join(member.value for member in models.TaskPriorityEnum)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority. Valid values: {valid}",
            )
        return value

    def _normalize_tags(self, tags: list[str] | None) -> list[str]:
        if tags is None:
            return []
        if not isinstance(tags, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tags must be provided as a list of strings",
            )
        normalized: list[str] = []
        for tag in tags:
            if not isinstance(tag, str):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Each tag must be a string",
                )
            stripped = tag.strip()
            if stripped:
                normalized.append(stripped)
        return normalized

