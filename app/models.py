from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    department = Column(String(100))
    role = Column(String(100))
    date_joined = Column(DateTime, default=func.now(), nullable=False)
    #updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Add composite index for common queries
    __table_args__ = (
        Index('idx_department_role', 'department', 'role'),
    )