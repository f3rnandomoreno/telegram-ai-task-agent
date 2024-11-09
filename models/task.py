from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from utils.database import Base

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    assignee = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    status = Column(String, nullable=False, default='TODO')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con el usuario
    assigned_user = relationship("User", back_populates="tasks") 