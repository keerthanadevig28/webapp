from pydantic import BaseModel, EmailStr, Field, field_validator, field_serializer
from typing import Optional
from datetime import datetime
from uuid import UUID
import re


# ─── User Schemas (existing) ───

class UserCreate(BaseModel):
    username: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    account_created: Optional[datetime] = None
    account_updated: Optional[datetime] = None

    class Config:
        extra = "ignore"


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    password: Optional[str] = Field(None, min_length=8)

    class Config:
        extra = "forbid"

    @field_validator('first_name', 'last_name', 'password')
    def check_at_least_one_field(cls, v, info):
        return v


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    account_created: datetime
    account_updated: datetime

    @field_serializer('id')
    def serialize_id(self, value: UUID) -> str:
        return str(value)

    class Config:
        from_attributes = True


# ─── Course Schemas ───

DEPT_CODE_REGEX = re.compile(r"^[A-Z]{2,6}$")
VALID_CLASSIFICATIONS = {"core", "elective"}

# Fields that the client must NEVER send (server-generated)
COURSE_READONLY_FIELDS = {"id", "has_syllabus", "date_created", "date_updated"}

# Fields that cannot be changed on update
COURSE_IMMUTABLE_FIELDS = {"id", "department_code", "number", "has_syllabus", "date_created", "date_updated"}

# Fields that can be updated
COURSE_UPDATABLE_FIELDS = {"title", "credit_hours", "classification", "description", "prerequisites"}


class CourseCreateRequest(BaseModel):
    department_code: str
    number: str
    title: str
    credit_hours: int
    classification: str
    description: Optional[str] = None
    prerequisites: Optional[str] = None

    @field_validator("department_code")
    @classmethod
    def validate_dept_code(cls, v):
        if not DEPT_CODE_REGEX.match(v):
            raise ValueError("department_code must be 2-6 uppercase letters")
        return v

    @field_validator("number")
    @classmethod
    def validate_number(cls, v):
        if not (1 <= len(v) <= 6):
            raise ValueError("number must be 1-6 characters")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not (1 <= len(v) <= 255):
            raise ValueError("title must be 1-255 characters")
        return v

    @field_validator("credit_hours")
    @classmethod
    def validate_credit_hours(cls, v):
        if not (1 <= v <= 8):
            raise ValueError("credit_hours must be between 1 and 8")
        return v

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, v):
        if v not in VALID_CLASSIFICATIONS:
            raise ValueError("classification must be 'core' or 'elective'")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None and len(v) > 2000:
            raise ValueError("description must be at most 2000 characters")
        return v

    @field_validator("prerequisites")
    @classmethod
    def validate_prerequisites(cls, v):
        if v is not None and len(v) > 512:
            raise ValueError("prerequisites must be at most 512 characters")
        return v

    class Config:
        extra = "forbid"


class CourseResponse(BaseModel):
    id: UUID
    department_code: str
    number: str
    title: str
    credit_hours: int
    classification: str
    description: Optional[str] = None
    prerequisites: Optional[str] = None
    has_syllabus: bool
    date_created: datetime
    date_updated: datetime

    @field_serializer('id')
    def serialize_id(self, value: UUID) -> str:
        return str(value)

    class Config:
        from_attributes = True


class SyllabusResponse(BaseModel):
    id: UUID
    course_id: UUID
    file_name: str
    s3_bucket_name: str
    s3_object_key: str
    content_type: str
    file_size: int
    url: str
    date_created: datetime
    date_updated: datetime

    @field_serializer('id', 'course_id')
    def serialize_uuids(self, value: UUID) -> str:
        return str(value)

    class Config:
        from_attributes = True