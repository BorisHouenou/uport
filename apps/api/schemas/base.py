"""Shared Pydantic base models."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UportaiBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TimestampMixin(UportaiBase):
    created_at: datetime
    updated_at: datetime | None = None


class TaskResponse(UportaiBase):
    task_id: str
    status: str
