from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from uuid import UUID

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Course
from app.schemas import (
    CourseCreateRequest, CourseResponse,
    COURSE_IMMUTABLE_FIELDS, COURSE_UPDATABLE_FIELDS, COURSE_READONLY_FIELDS,
    VALID_CLASSIFICATIONS
)

router = APIRouter(prefix="/v1/courses", tags=["Courses"])


def validate_content_type(request: Request):
    """Ensure Content-Type is application/json for POST/PUT."""
    ct = request.headers.get("content-type", "")
    if "application/json" not in ct:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Content-Type must be application/json"
        )


# ─── GET /v1/courses ───
@router.get("", response_model=list[CourseResponse])
def list_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    courses = db.query(Course).order_by(Course.department_code.asc(), Course.number.asc()).all()
    return [CourseResponse.model_validate(c) for c in courses]


# ─── POST /v1/courses ───
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_course(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_content_type(request)

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body")

    if not body or not isinstance(body, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body is required")

    # Reject readonly fields sent by client
    for field in COURSE_READONLY_FIELDS:
        if field in body:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field}' cannot be set by the client"
            )

    # Validate with Pydantic schema
    try:
        course_data = CourseCreateRequest(**body)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    now = datetime.now(timezone.utc)
    course = Course(
        department_code=course_data.department_code,
        number=course_data.number,
        title=course_data.title,
        credit_hours=course_data.credit_hours,
        classification=course_data.classification,
        description=course_data.description,
        prerequisites=course_data.prerequisites,
        has_syllabus=False,
        date_created=now,
        date_updated=now,
    )

    try:
        db.add(course)
        db.commit()
        db.refresh(course)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Course with department_code '{course_data.department_code}' and number '{course_data.number}' already exists"
        )

    response = JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=CourseResponse.model_validate(course).model_dump(mode="json"),
    )
    response.headers["Location"] = f"/v1/courses/{course.id}"
    return response


# ─── GET /v1/courses/{course_id} ───
@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return CourseResponse.model_validate(course)


# ─── PUT /v1/courses/{course_id} ───
@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_content_type(request)

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body")

    if not body or not isinstance(body, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body cannot be empty")

    # Check for immutable fields
    for field in body:
        if field in COURSE_IMMUTABLE_FIELDS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field}' is immutable and cannot be updated"
            )

    # Check at least one updatable field
    updatable_provided = {k: v for k, v in body.items() if k in COURSE_UPDATABLE_FIELDS}
    if not updatable_provided:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one updatable field must be provided"
        )

    # Check for unknown fields
    unknown = set(body.keys()) - COURSE_UPDATABLE_FIELDS
    if unknown:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown field(s): {', '.join(unknown)}"
        )

    # Validate individual fields
    if "title" in updatable_provided:
        v = updatable_provided["title"]
        if not isinstance(v, str) or not (1 <= len(v) <= 255):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title must be 1-255 characters")

    if "credit_hours" in updatable_provided:
        v = updatable_provided["credit_hours"]
        if not isinstance(v, int) or not (1 <= v <= 8):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="credit_hours must be between 1 and 8")

    if "classification" in updatable_provided:
        v = updatable_provided["classification"]
        if v not in VALID_CLASSIFICATIONS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="classification must be 'core' or 'elective'")

    if "description" in updatable_provided:
        v = updatable_provided["description"]
        if v is not None and (not isinstance(v, str) or len(v) > 2000):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="description must be at most 2000 characters")

    if "prerequisites" in updatable_provided:
        v = updatable_provided["prerequisites"]
        if v is not None and (not isinstance(v, str) or len(v) > 512):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="prerequisites must be at most 512 characters")

    # Apply updates
    for field, value in updatable_provided.items():
        setattr(course, field, value)

    course.date_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(course)

    return CourseResponse.model_validate(course)


# ─── DELETE /v1/courses/{course_id} ───
@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if course.has_syllabus:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete course with an attached syllabus. Delete the syllabus first."
        )

    db.delete(course)
    db.commit()
    return None