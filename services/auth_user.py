from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User

pwd_context = CryptContext(schemes=["bcrypt"])

async def user_sign_in(name: str, password: str, db: AsyncSession):
    hashed_password = pwd_context.hash(password)
    new_user = User(name=name, password=hashed_password)  # 2. cria o objeto
    db.add(new_user)                                # 3. adiciona na sessão
    await db.commit()                               # 4. salva no banco
    return new_user

async def user_login(name: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.name == name))
    user = result.scalars().first()
    if not user:
        return None
    if pwd_context.verify(password, user.password):
        return user
    return None