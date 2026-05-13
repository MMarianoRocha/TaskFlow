from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database.base import Base


class Pomodoro(Base):
    __tablename__ = "pomodoros"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    status = Column(String, nullable=False, default="working")
    active = Column(Boolean, default=True, nullable=False)
    duration = Column(Integer, default=25, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="pomodoros")
