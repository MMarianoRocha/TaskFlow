from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
from models.user import User
from models.task import Task

DATABASE_URL = "sqlite:///./task_app.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(engine, autocommit=False, autoflush=False)

Base.metadata.create_all(bind=engine)

with SessionLocal() as session:
    # user = session.add(Task(title="Bumbarabaum", description="Tarefa de teste", completed=False, user_id=2))
    # session.commit()
    user = session.query(User).filter_by(name="Matheus").first()
    if user:
        print(f"Usuário encontrado: {user.name}")
        for task in user.tasks:
            print(f"- Tarefa: {task.title}, Concluída: {task.completed}")