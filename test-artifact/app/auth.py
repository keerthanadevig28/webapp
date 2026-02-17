import bcrypt
import base64
from fastapi import HTTPException, status, Depends, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

def hash_password(password: str) -> str:
    """Hash password using BCrypt with salt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against BCrypt hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def decode_basic_auth(authorization: str) -> tuple:
    """Decode Basic Auth header"""
    try:
        encoded = authorization.replace('Basic ', '')
        decoded = base64.b64decode(encoded).decode('utf-8')
        email, password = decoded.split(':', 1)
        return email, password
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from Basic Auth header.
    Used for protected endpoints.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    if not authorization.startswith('Basic '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    email, password = decode_basic_auth(authorization)
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user