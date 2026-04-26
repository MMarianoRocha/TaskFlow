from pydantic import BaseModel, ConfigDict, Field

class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., example="DarkDemon14", min_length=3, max_length=30)
    password: str = Field(..., example="minhasenha", min_length=6, max_length=72, description="A senha deve conter pelo menos uma letra e um número")

class UserLogin(BaseModel):
    name: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str