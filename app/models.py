from sqlalchemy import (
    Column, String, DateTime, BigInteger, Boolean, Integer,
    Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    verified = Column(Boolean, nullable=False, default=False)
    account_created = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    account_updated = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def username(self):
        """Alias for email - username is the email"""
        return self.email

    def to_dict(self):
        """Convert user to dictionary (excludes password)"""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "account_created": self.account_created.isoformat(),
            "account_updated": self.account_updated.isoformat()
        }


class HealthCheck(Base):
    __tablename__ = "health_checks"

    check_id = Column(BigInteger, primary_key=True, autoincrement=True)
    check_datetime = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_code = Column(String(6), nullable=False)
    number = Column(String(6), nullable=False)
    title = Column(String(255), nullable=False)
    credit_hours = Column(Integer, nullable=False)
    classification = Column(String(20), nullable=False)  # 'core' or 'elective'
    description = Column(Text, nullable=True)
    prerequisites = Column(String(512), nullable=True)
    has_syllabus = Column(Boolean, nullable=False, default=False)
    date_created = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    date_updated = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationship to syllabus (one-to-one)
    syllabus = relationship("Syllabus", back_populates="course", uselist=False, cascade="all, delete-orphan")

    # Unique constraint on department_code + number
    __table_args__ = (
        UniqueConstraint('department_code', 'number', name='uq_course_dept_number'),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "department_code": self.department_code,
            "number": self.number,
            "title": self.title,
            "credit_hours": self.credit_hours,
            "classification": self.classification,
            "description": self.description,
            "prerequisites": self.prerequisites,
            "has_syllabus": self.has_syllabus,
            "date_created": self.date_created.isoformat(),
            "date_updated": self.date_updated.isoformat()
        }


class Syllabus(Base):
    __tablename__ = "syllabi"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, unique=True)
    file_name = Column(String(255), nullable=False)
    s3_bucket_name = Column(String(255), nullable=False)
    s3_object_key = Column(String(1024), nullable=False)
    content_type = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    url = Column(String(1024), nullable=False)
    date_created = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    date_updated = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationship back to course
    course = relationship("Course", back_populates="syllabus")

    def to_dict(self):
        return {
            "id": str(self.id),
            "course_id": str(self.course_id),
            "file_name": self.file_name,
            "s3_bucket_name": self.s3_bucket_name,
            "s3_object_key": self.s3_object_key,
            "content_type": self.content_type,
            "file_size": self.file_size,
            "url": self.url,
            "date_created": self.date_created.isoformat(),
            "date_updated": self.date_updated.isoformat()
        }