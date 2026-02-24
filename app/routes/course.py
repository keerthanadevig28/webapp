from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from uuid import UUID

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Course
from app.errors import error_response
from app.schemas import (
    CourseCreateRequest, CourseResponse,
    COURSE_IMMUTABLE_FIELDS, COURSE_UPDATABLE_FIELDS, COURSE_READONLY_FIELDS,
    VALID_CLASSIFICATIONS
)

router = APIRouter(prefix="/v1/courses", tags=["Courses"])


def validate_content_type(request: Request):
    ct = request.headers.get("content-type", "")
    if "application/json" not in ct:
        return error_response(415, "Unsupported Media Type", "Content-Type must be application/json", request.url.path)
    return None


# ─── GET /v1/courses ───
@router.get("")
def list_courses(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    courses = db.query(Course).order_by(Course.department_code.asc(), Course.number.asc()).all()
    return [CourseResponse.model_validate(c).model_dump(mode="json") for c in courses]


# ─── POST /v1/courses ───
@router.post("")
async def create_course(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    path = request.url.path

    # Check content type
    ct_error = validate_content_type(request)
    if ct_error:
        return ct_error

    try:
        body = await request.json()
    except Exception:
        return error_response(400, "Bad Request", "Invalid or malformed JSON body", path)

    if not body or not isinstance(body, dict):
        return error_response(400, "Bad Request", "Request body is required", path)

    # Reject readonly fields sent by client
    for field in COURSE_READONLY_FIELDS:
        if field in body:
            return error_response(400, "Bad Request", f"Field '{field}' cannot be set by the client", path)

    # Validate with Pydantic schema
    try:
        course_data = CourseCreateRequest(**body)
    except Exception as e:
        return error_response(400, "Validation Error", str(e), path)

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
        return error_response(
            409, "Conflict",
            f"Course {course_data.department_code} {course_data.number} already exists",
            path
        )

    response = JSONResponse(
        status_code=201,
        content=CourseResponse.model_validate(course).model_dump(mode="json"),
    )
    response.headers["Location"] = f"/v1/courses/{course.id}"
    return response


# ─── GET /v1/courses/{course_id} ───
@router.get("/{course_id}")
def get_course(
    course_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return error_response(404, "Not Found", "Course not found", request.url.path)
    return CourseResponse.model_validate(course).model_dump(mode="json")


# ─── PUT /v1/courses/{course_id} ───
@router.put("/{course_id}")
async def update_course(
    course_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    path = request.url.path

    ct_error = validate_content_type(request)
    if ct_error:
        return ct_error

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return error_response(404, "Not Found", "Course not found", path)

    try:
        body = await request.json()
    except Exception:
        return error_response(400, "Bad Request", "Invalid or malformed JSON body", path)

    if not body or not isinstance(body, dict):
        return error_response(400, "Bad Request", "Request body cannot be empty", path)

    # Check for immutable fields
    for field in body:
        if field in COURSE_IMMUTABLE_FIELDS:
            return error_response(400, "Bad Request", f"Field '{field}' cannot be updated", path)

    # Check at least one updatable field
    updatable_provided = {k: v for k, v in body.items() if k in COURSE_UPDATABLE_FIELDS}
    if not updatable_provided:
        return error_response(400, "Bad Request", "At least one updatable field must be provided", path)

    # Check for unknown fields
    unknown = set(body.keys()) - COURSE_UPDATABLE_FIELDS
    if unknown:
        return error_response(400, "Bad Request", f"Unknown field(s): {', '.join(unknown)}", path)

    # Validate individual fields
    if "title" in updatable_provided:
        v = updatable_provided["title"]
        if not isinstance(v, str) or not (1 <= len(v) <= 255):
            return error_response(400, "Validation Error", "title must be 1-255 characters", path)

    if "credit_hours" in updatable_provided:
        v = updatable_provided["credit_hours"]
        if not isinstance(v, int) or not (1 <= v <= 8):
            return error_response(400, "Validation Error", "credit_hours must be between 1 and 8", path)

    if "classification" in updatable_provided:
        v = updatable_provided["classification"]
        if v not in VALID_CLASSIFICATIONS:
            return error_response(400, "Validation Error", "classification must be 'core' or 'elective'", path)

    if "description" in updatable_provided:
        v = updatable_provided["description"]
        if v is not None and (not isinstance(v, str) or len(v) > 2000):
            return error_response(400, "Validation Error", "description must be at most 2000 characters", path)

    if "prerequisites" in updatable_provided:
        v = updatable_provided["prerequisites"]
        if v is not None and (not isinstance(v, str) or len(v) > 512):
            return error_response(400, "Validation Error", "prerequisites must be at most 512 characters", path)

    # Apply updates
    for field, value in updatable_provided.items():
        setattr(course, field, value)

    course.date_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(course)

    return CourseResponse.model_validate(course).model_dump(mode="json")


# ─── DELETE /v1/courses/{course_id} ───
@router.delete("/{course_id}")
def delete_course(
    course_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    path = request.url.path
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return error_response(404, "Not Found", "Course not found", path)

    if course.has_syllabus:
        return error_response(
            409, "Conflict",
            f"Cannot delete course {course.department_code} {course.number} because it has a syllabus attached. Delete the syllabus first.",
            path
        )

    db.delete(course)
    db.commit()
    return JSONResponse(status_code=204, content=None)