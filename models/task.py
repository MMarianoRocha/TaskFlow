from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import backref, declarative_base, relationship
from database.base import Base

class Task(Base):
    __tablename__ = "tarefas"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    completed = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    user = relationship("User", back_populates="tasks")