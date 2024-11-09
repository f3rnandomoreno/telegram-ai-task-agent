from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from utils.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    userId = Column(String, unique=True, nullable=False)
    chatId = Column(String, nullable=False)
    userName = Column(String)
    firstName = Column(String)
    lastName = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con las tareas
    tasks = relationship("Task", back_populates="assigned_user") 