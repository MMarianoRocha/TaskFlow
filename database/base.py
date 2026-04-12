from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import backref, declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    password = Column(String, nullable=False)

    tasks = relationship("Task", backref="user")

class Task(Base):
    __tablename__ = "tarefas"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    completed = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("usuarios.id"))