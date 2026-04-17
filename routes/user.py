from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.concurrency import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["users"])

users = {
    1: {"name": "Matheus", "password": "123456"},
    2: {"name": "João", "password": "abcdef"},
    3: {"name": "Maria", "password": "qwerty"},
    4: {"name": "Ana", "password": "pass123"},
    5: {"name": "Carlos", "password": "abc123"}
}

# region Get
@router.get("") # GET /users
def get_all_users(limit: int = 10):
    if limit:
        return {"users": list(users.values())[:limit]}
    return users

@router.get("/{id}")
def get_user(id: int):
    if id not in users:
        raise HTTPException(status_code=404, detail="User não encontrado")
    return users.get(id)
# endregion