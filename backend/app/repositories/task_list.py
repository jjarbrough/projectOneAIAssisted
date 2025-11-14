from __future__ import annotations

from sqlalchemy.orm import Session

from app.db import models


class TaskListRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, name: str, owner_id: int) -> models.TaskList:
        task_list = models.TaskList(name=name, owner_id=owner_id)
        self.session.add(task_list)
        self.session.commit()
        self.session.refresh(task_list)
        return task_list

    def get_by_id(self, list_id: int) -> models.TaskList | None:
        return self.session.query(models.TaskList).filter(models.TaskList.id == list_id).first()

    def list_for_user(self, owner_id: int) -> list[models.TaskList]:
        return (
            self.session.query(models.TaskList)
            .filter(models.TaskList.owner_id == owner_id)
            .order_by(models.TaskList.created_at.asc())
            .all()
        )

