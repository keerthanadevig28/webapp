from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.auth import hash_password, get_current_user

router = APIRouter()

@router.post("/v1/user", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    
    Requirements:
    - Email must be unique
    - Password must be BCrypt hashed
    - account_created and account_updated set automatically (ignore user input)
    - Password never returned in response
    - Return 201 on success, 400 if email exists or validation fails
    """
    
    existing_user = db.query(User).filter(User.email == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    hashed_password = hash_password(user_data.password)
    
    new_user = User(
        email=user_data.username,
        password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

@router.get("/v1/user/self", response_model=UserResponse)
def get_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user's information.
    
    Requirements:
    - Requires Basic Auth
    - Returns user info without password
    - Return 200 on success, 401 if not authenticated
    """
    return current_user

@router.put("/v1/user/self", status_code=status.HTTP_204_NO_CONTENT)
def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's information.
    
    Requirements:
    - Requires Basic Auth
    - Only first_name, last_name, password can be updated
    - account_updated automatically updated to current timestamp
    - Password must be BCrypt hashed if provided
    - Return 204 on success, 400 if invalid fields, 401 if not authenticated
    """

    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be updated"
        )
    
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    
    if user_update.password is not None:
        current_user.password = hash_password(user_update.password)
    
    current_user.account_updated = datetime.now(timezone.utc)
    
    try:
        db.commit()
        return None  
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )