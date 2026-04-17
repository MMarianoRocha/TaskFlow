from pydantic import BaseModel, ConfigDict, Field

class TaskCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str = Field(..., example="Task Title", min_length=3, max_length=30)
    description: str = Field(..., example="Task Description", min_length=3, max_length=100)

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    completed: bool
