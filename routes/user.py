from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.concurrency import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User
from database.session import get_async_session
from schemas.user import UserCreate, UserLogin ,UserResponse
from services.auth_user import user_login, user_sign_in

router = APIRouter(prefix="/users", tags=["users"])

# region Get
@router.get("") # GET /users
async def get_all_users(limit: int = 10, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(User).limit(limit))
    users = result.scalars().all()
    return users

@router.get("/{id}")
async def get_user(id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User não encontrado")
    return user
# endregion

# region Post
@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    existing = await user_login(user.name, user.password, db)
    if existing:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    new_user = await user_sign_in(user.name, user.password, db)
    return new_user
    
@router.post("/login")
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_async_session)):
    user_obj = await user_login(user.name, user.password, db)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {"message": "Login bem-sucedido"}
# endregion