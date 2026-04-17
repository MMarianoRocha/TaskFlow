from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from schemas.task import TaskCreate, TaskResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_async_session, create_db_and_tables
# Importar os modelos para que o SQLAlchemy os registre
from models.task import Task
from models.user import User
# Routers
from routes.task import router as task_router
from routes.user import router as user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(
    title="Task API",
    description="API para gerenciamento de tarefas em conjunto com FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(task_router)
app.include_router(user_router)