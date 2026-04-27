from select import select
from sqlalchemy import select

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from database.session import get_async_session
from models.task import Task
from schemas.task import TaskCreate, TaskResponse
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.task import TaskCreate, TaskResponse
from services.auth_user import user_login

router = APIRouter(prefix="/tasks", tags=["tasks"])

async def get_current_user(name: str, password: str, db: AsyncSession = Depends(get_async_session)):
    user = await user_login(name, password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    return user

@router.get("", response_model=list[TaskResponse])
async def get_all_tasks(
    limit: int = 10,
    user_name: str = None,
    user_password: str = None,
    db: AsyncSession = Depends(get_async_session)
):
    current_user = await get_current_user(user_name, user_password, db)
    result = await db.execute(select(Task).where(Task.user_id == current_user.id).limit(limit))
    tasks = result.scalars().all()
    return tasks

@router.get("/{id}", response_model=TaskResponse)
async def get_task(id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Task).where(Task.id == id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    return task
# endregion

# region Post
@router.post("", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_async_session)):
    new_task = Task(title=task.title, description=task.description, completed=False)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task
# endregion

# region Put
@router.put("/{id}")
async def update_task(id: int, task: TaskCreate, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Task).where(Task.id == id))
    existing_task = result.scalar_one_or_none()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    for key, value in task.dict().items():
        setattr(existing_task, key, value)
    await db.commit()
    await db.refresh(existing_task)
    return existing_task
# endregion

# region Delete
@router.delete("/{id}")
async def delete_task(id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Task).where(Task.id == id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    await db.delete(task)
    await db.commit()
    return {"detail": "Task deletada com sucesso"}
# endregion