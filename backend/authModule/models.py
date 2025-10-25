from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

current_user_email = None

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    password = Column(String, nullable=False)
    last_updated = Column(String, nullable=True)  # NEW: Store as ISO string

class HealthRecord(Base):
    __tablename__ = 'health_records'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    problem = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    reported_on = Column(String, nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
