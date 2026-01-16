from sqlalchemy.orm import Session
from app import models, schemas
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def get_employees(db: Session, skip: int = 0, limit: int = 10, department: str = None, role: str = None):
    query = db.query(models.Employee)
    if department:
        query = query.filter(models.Employee.department == department)
    if role:
        query = query.filter(models.Employee.role == role)
    return query.offset(skip).limit(limit).all()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(**employee.dict())
    try:
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")

def update_employee(db: Session, employee_id: int, employee: schemas.EmployeeUpdate):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    update_data = employee.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)
    try:
        db.commit()
        db.refresh(db_employee)
        return db_employee
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")

def delete_employee(db: Session, employee_id: int):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(db_employee)
    db.commit()
    return db_employee