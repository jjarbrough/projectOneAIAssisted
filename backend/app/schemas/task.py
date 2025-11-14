from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskListCreate(BaseModel):
    name: str


class TaskListRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: date | None = None
    status: TaskStatus = TaskStatus.pending
    priority: TaskPriority = TaskPriority.medium
    tags: list[str] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: date | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    tags: list[str] | None = None


class TaskRead(BaseModel):
    id: int
    list_id: int
    title: str
    description: str | None = None
    due_date: date | None = None
    status: TaskStatus
    priority: TaskPriority
    tags: list[str]
    position: int

    model_config = ConfigDict(from_attributes=True)


class TaskReorderRequest(BaseModel):
    task_ids: list[int]

