from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from database.session import create_db_and_tables

# Importar os modelos para que o SQLAlchemy os registre
from models.user import User
from models.pomodoro import Pomodoro

# Routers
from routes.user import router as user_router
from routes.pomodoro import router as pomodoro_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(
    title="PomodoroHub API",
    description="API para gerenciamento de sessões Pomodoro com FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(user_router)
app.include_router(pomodoro_router)