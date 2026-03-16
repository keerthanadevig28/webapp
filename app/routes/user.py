from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.auth import hash_password, get_current_user
from app.logger import logger
from app.metrics import count, timed

router = APIRouter()

@router.post("/v1/user", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    count("api.create_user")
    logger.info("POST /v1/user called", extra={"email": user_data.username})
    with timed("api.create_user.time"):
        with timed("db.check_existing_user"):
            existing_user = db.query(User).filter(User.email == user_data.username).first()
        if existing_user:
            logger.warning("User creation failed — email already exists",
                extra={"email": user_data.username})
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
            with timed("db.create_user"):
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
            logger.info("User created successfully", extra={"email": user_data.username})
            return new_user
        except IntegrityError:
            db.rollback()
            logger.warning("User creation failed — integrity error",
                extra={"email": user_data.username})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

@router.get("/v1/user/self", response_model=UserResponse)
def get_user_info(current_user: User = Depends(get_current_user)):
    count("api.get_user_self")
    logger.info("GET /v1/user/self called", extra={"email": current_user.email})
    # ✅ ADDED: api timer + db timer
    with timed("api.get_user_self.time"):
        with timed("db.get_user_self"):
            return current_user

@router.put("/v1/user/self", status_code=status.HTTP_204_NO_CONTENT)
def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    count("api.update_user_self")
    logger.info("PUT /v1/user/self called", extra={"email": current_user.email})
    with timed("api.update_user_self.time"):
        update_data = user_update.model_dump(exclude_unset=True)
        if not update_data:
            logger.warning("Update user failed — no fields provided",
                extra={"email": current_user.email})
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
            with timed("db.update_user"):
                db.commit()
            logger.info("User updated successfully", extra={"email": current_user.email})
            return None
        except Exception as e:
            db.rollback()
            logger.error("User update failed",
                extra={"email": current_user.email, "error": str(e)}, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update user"
            )