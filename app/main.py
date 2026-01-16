from fastapi import Depends, FastAPI, HTTPException, Query, status
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, models, schemas, auth
from app.database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user["username"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/employees/", response_model=schemas.Employee, status_code=201)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    if not employee.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    return crud.create_employee(db=db, employee=employee)

@app.get("/api/employees/", response_model=List[schemas.Employee])
def read_employees(page: int = 1, limit: int = Query(default=10, le=10), department: Optional[str] = None, role: Optional[str] = None, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    skip = (page - 1) * limit
    employees = crud.get_employees(db, skip=skip, limit=limit, department=department, role=role)
    return employees

@app.get("/api/employees/{employee_id}/", response_model=schemas.Employee)
def read_employee(employee_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.put("/api/employees/{employee_id}/", response_model=schemas.Employee)
def update_employee(employee_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    if employee.name is not None and not employee.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    return crud.update_employee(db=db, employee_id=employee_id, employee=employee)

@app.delete("/api/employees/{employee_id}/", status_code=204)
def delete_employee(employee_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    crud.delete_employee(db=db, employee_id=employee_id)
    return