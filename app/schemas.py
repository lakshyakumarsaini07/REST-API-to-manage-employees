from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is not None:
            if not any(char.isdigit() for char in v):
                raise ValueError('Password must contain at least one digit')
            if not any(char.isupper() for char in v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not any(char.islower() for char in v):
                raise ValueError('Password must contain at least one lowercase letter')
        return v

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserInDB(User):
    hashed_password: str

# Employee Schemas
class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    department: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=100)

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    date_joined: datetime
    #updated_at: Optional[datetime] = None

class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=100)

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    
# Response Schemas
class EmployeeList(BaseModel):
    total: int
    page: int
    limit: int
    employees: list[Employee]
    
class Message(BaseModel):
    message: str