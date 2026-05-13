from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PomodoroControl(BaseModel):
    name: str
    password: str
    duration: int = Field(default=25, gt=0, description="Duração em minutos")


class PomodoroStop(BaseModel):
    name: str
    password: str


class PomodoroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    status: str
    active: bool
    duration: int
    started_at: datetime
    ended_at: datetime | None


class PomodoroActiveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    status: str
    duration: int
    started_at: datetime
    user_name: str
