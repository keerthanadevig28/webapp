from pydantic import BaseModel, EmailStr, Field, field_validator, field_serializer
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: EmailStr 
    password: str = Field(..., min_length=8)  
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    account_created: Optional[datetime] = None
    account_updated: Optional[datetime] = None
    
    class Config:
        extra = "ignore" 

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    password: Optional[str] = Field(None, min_length=8) 
    
    class Config:
        extra = "forbid"
    
    @field_validator('first_name', 'last_name', 'password')
    def check_at_least_one_field(cls, v, info):
        return v

class UserResponse(BaseModel):
    """Schema for user response (no password)"""
    id: UUID
    username: str  

    email: str     
    first_name: str
    last_name: str
    account_created: datetime
    account_updated: datetime
    
    @field_serializer('id')
    def serialize_id(self, value: UUID) -> str:
        """Convert UUID to string for JSON serialization"""
        return str(value)
    
    class Config:
        from_attributes = True
