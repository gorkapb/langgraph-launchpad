from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from langgraph_launchpad.core.database import Base


class Thread(Base):
    """Thread model for storing conversation threads."""
    
    __tablename__ = "threads"
    
    thread_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    def __repr__(self) -> str:
        return f"<Thread(id={self.thread_id}, user_id='{self.user_id}')>"