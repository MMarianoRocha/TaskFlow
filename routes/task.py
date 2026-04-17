from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from schemas.task import TaskCreate, TaskResponse
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.task import TaskCreate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])

tasks = {
    1: {"title": "Comprar leite", "description": "Ir ao supermercado e comprar leite", "completed": False},
    2: {"title": "Fazer exercício", "description": "Fazer 30 minutos de exercício", "completed": False},
    3: {"title": "Enviar email", "description": "Enviar email para o cliente", "completed": True},
    4: {"title": "Ler livro", "description": "Ler 2 capítulos do livro", "completed": False},
    5: {"title": "Limpar casa", "description": "Limpar e organizar a sala", "completed": True}
}

# region Get
@router.get("")
def get_all_tasks(limit: int = 10):
    if limit:
        return {"tasks": list(tasks.values())[:limit]}
    return tasks

@router.get("/{id}", response_model=TaskResponse)
def get_task(id: int):
    if id not in tasks:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    return tasks.get(id)
# endregion

# region Post
@router.post("", response_model=TaskResponse)
def create_task(task: TaskCreate):
    new_task = {"title": task.title, "description": task.description, "completed": False}
    tasks[max(tasks.keys()) + 1] = new_task
    return new_task
# endregion

# region Put
@router.put("/{id}")
def update_task(id: int, task: TaskCreate):
    if id not in tasks:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    updated_task = {"title": task.title, "description": task.description, "completed": tasks[id]["completed"]}
    tasks[id] = updated_task
    return updated_task
# endregion

# region Delete
@router.delete("/{id}")
def delete_task(id: int):
    if id not in tasks:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    del tasks[id]
    return {"detail": "Task deletada com sucesso"}
# endregion