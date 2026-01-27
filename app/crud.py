from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func, or_
from typing import Optional, List
from fastapi import HTTPException, status
import logging
from app import models, schemas

logger = logging.getLogger(__name__)

# Employee CRUD Operations
def get_employee(db: Session, employee_id: int) -> Optional[models.Employee]:
    """Get employee by ID"""
    try:
        return db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error getting employee {employee_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

def get_employees(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    department: Optional[str] = None,
    role: Optional[str] = None,
    search: Optional[str] = None
) -> List[models.Employee]:
    """Get employees with filtering and pagination"""
    try:
        query = db.query(models.Employee)
        
        # Apply filters
        if department:
            query = query.filter(models.Employee.department.ilike(f"%{department}%"))
        if role:
            query = query.filter(models.Employee.role.ilike(f"%{role}%"))
        if search:
            query = query.filter(
                or_(
                    models.Employee.name.ilike(f"%{search}%"),
                    models.Employee.email.ilike(f"%{search}%")
                )
            )
        
        # Apply pagination
        return query.order_by(models.Employee.id).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error getting employees: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

def get_employees_count(
    db: Session,
    department: Optional[str] = None,
    role: Optional[str] = None,
    search: Optional[str] = None
) -> int:
    """Get total count of employees with filters"""
    try:
        query = db.query(func.count(models.Employee.id))
        
        if department:
            query = query.filter(models.Employee.department.ilike(f"%{department}%"))
        if role:
            query = query.filter(models.Employee.role.ilike(f"%{role}%"))
        if search:
            query = query.filter(
                or_(
                    models.Employee.name.ilike(f"%{search}%"),
                    models.Employee.email.ilike(f"%{search}%")
                )
            )
        
        return query.scalar()
    except SQLAlchemyError as e:
        logger.error(f"Database error counting employees: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

def create_employee(db: Session, employee: schemas.EmployeeCreate) -> models.Employee:
    """Create a new employee"""
    try:
        # Check if email already exists
        existing_employee = db.query(models.Employee).filter(
            models.Employee.email == employee.email
        ).first()
        
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        db_employee = models.Employee(**employee.model_dump())
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        logger.info(f"Created employee: {db_employee.id} - {db_employee.email}")
        return db_employee
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating employee: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating employee: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

def update_employee(
    db: Session,
    employee_id: int,
    employee: schemas.EmployeeUpdate
) -> models.Employee:
    """Update an employee"""
    try:
        db_employee = get_employee(db, employee_id)
        if not db_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Check if email is being changed and if it already exists
        update_data = employee.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"] != db_employee.email:
            existing_employee = db.query(models.Employee).filter(
                models.Employee.email == update_data["email"],
                models.Employee.id != employee_id
            ).first()
            
            if existing_employee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        for key, value in update_data.items():
            setattr(db_employee, key, value)
        
        db.commit()
        db.refresh(db_employee)
        logger.info(f"Updated employee: {db_employee.id}")
        return db_employee
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating employee {employee_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating employee {employee_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

def delete_employee(db: Session, employee_id: int) -> bool:
    """Delete an employee"""
    try:
        db_employee = get_employee(db, employee_id)
        if not db_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        db.delete(db_employee)
        db.commit()
        logger.info(f"Deleted employee: {employee_id}")
        return True
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting employee {employee_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

# User CRUD Operations
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    try:
        return db.query(models.User).filter(models.User.id == user_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error getting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

def get_users(db: Session, skip: int = 0, limit: int = 10) -> List[models.User]:
    """Get all users with pagination"""
    try:
        return db.query(models.User).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error getting users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

def update_user(db: Session, user_id: int, user: schemas.UserUpdate) -> models.User:
    """Update a user"""
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_data = user.model_dump(exclude_unset=True)
        
        # Handle password update separately
        if "password" in update_data:
            from app.auth import get_password_hash
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        logger.info(f"Updated user: {db_user.id}")
        return db_user
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )