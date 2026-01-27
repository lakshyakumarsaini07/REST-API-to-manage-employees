from fastapi import Depends, FastAPI, HTTPException, Query, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from app import crud, models, schemas, auth
from app.database import SessionLocal, engine, init_db
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    init_db()
    logger.info("Database initialized")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check if the API is running"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.api_version
    }

# Authentication Routes
@app.post("/api/auth/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        db_user = auth.create_user(db, user)
        logger.info(f"New user registered: {db_user.username}")
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@app.post("/api/auth/login", response_model=schemas.Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login to get access token"""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.username}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }

@app.get("/api/auth/me", response_model=schemas.User, tags=["Authentication"])
async def get_current_user_info(current_user: models.User = Depends(auth.get_current_active_user)):
    """Get current user information"""
    return current_user

# User Management Routes (Admin only)
@app.get("/api/users/", response_model=List[schemas.User], tags=["Users"])
async def list_users(
    skip: int = 0,
    limit: int = Query(default=10, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_superuser)
):
    """List all users (Admin only)"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/api/users/{user_id}", response_model=schemas.User, tags=["Users"])
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_superuser)
):
    """Get user by ID (Admin only)"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.put("/api/users/{user_id}", response_model=schemas.User, tags=["Users"])
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_superuser)
):
    """Update user (Admin only)"""
    return crud.update_user(db, user_id, user_update)

# Employee Routes
@app.post("/api/employees/", response_model=schemas.Employee, status_code=status.HTTP_201_CREATED, tags=["Employees"])
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create a new employee"""
    logger.info(f"Creating employee: {employee.email} by user: {current_user.username}")
    return crud.create_employee(db=db, employee=employee)

@app.get("/api/employees/", response_model=schemas.EmployeeList, tags=["Employees"])
def list_employees(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    department: Optional[str] = None,
    role: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get list of employees with pagination and filtering"""
    skip = (page - 1) * limit
    employees = crud.get_employees(
        db,
        skip=skip,
        limit=limit,
        department=department,
        role=role,
        search=search
    )
    total = crud.get_employees_count(
        db,
        department=department,
        role=role,
        search=search
    )
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "employees": employees
    }

@app.get("/api/employees/{employee_id}", response_model=schemas.Employee, tags=["Employees"])
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get employee by ID"""
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return db_employee

@app.put("/api/employees/{employee_id}", response_model=schemas.Employee, tags=["Employees"])
def update_employee(
    employee_id: int,
    employee: schemas.EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update an employee"""
    logger.info(f"Updating employee: {employee_id} by user: {current_user.username}")
    return crud.update_employee(db=db, employee_id=employee_id, employee=employee)

@app.delete("/api/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Employees"])
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Delete an employee"""
    logger.info(f"Deleting employee: {employee_id} by user: {current_user.username}")
    crud.delete_employee(db=db, employee_id=employee_id)
    return

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )