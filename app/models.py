from sqlalchemy import Column, String, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import UUID
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
