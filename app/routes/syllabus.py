from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid import UUID

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Course, Syllabus
from app.schemas import SyllabusResponse
from app.errors import error_response
from app.services.s3_service import upload_file_to_s3, delete_file_from_s3

router = APIRouter(prefix="/v1/courses/{course_id}/syllabus", tags=["Syllabus"])


def get_course_or_error(course_id: UUID, db: Session, path: str):
    """Returns (course, None) or (None, error_response)."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return None, error_response(404, "Not Found", "Course not found", path)
    return course, None


# ─── POST /v1/courses/{course_id}/syllabus ───
@router.post("")
async def upload_syllabus(
    course_id: UUID,
    request: Request,
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    path = request.url.path
    course, err = get_course_or_error(course_id, db, path)
    if err:
        return err

    # Check if syllabus already exists
    if course.has_syllabus:
        return error_response(
            409, "Conflict",
            f"Course {course.department_code} {course.number} already has a syllabus. Delete the existing syllabus first.",
            path
        )

    # Validate file
    if file is None:
        return error_response(400, "Bad Request", "A syllabus file must be provided in the 'file' form field", path)

    file_content = await file.read()

    if len(file_content) == 0:
        return error_response(400, "Bad Request", "Uploaded file is empty", path)

    # Upload to S3
    try:
        s3_result = upload_file_to_s3(
            file_content=file_content,
            course_id=str(course_id),
            original_filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
        )
    except Exception as e:
        return error_response(500, "Internal Server Error", f"Failed to upload file to S3: {str(e)}", path)

    now = datetime.now(timezone.utc)
    syllabus = Syllabus(
        course_id=course_id,
        file_name=file.filename,
        s3_bucket_name=s3_result["s3_bucket_name"],
        s3_object_key=s3_result["s3_object_key"],
        content_type=file.content_type or "application/octet-stream",
        file_size=s3_result["file_size"],
        url=s3_result["url"],
        date_created=now,
        date_updated=now,
    )

    db.add(syllabus)

    # Update course has_syllabus flag
    course.has_syllabus = True
    course.date_updated = now

    db.commit()
    db.refresh(syllabus)

    response = JSONResponse(
        status_code=201,
        content=SyllabusResponse.model_validate(syllabus).model_dump(mode="json"),
    )
    response.headers["Location"] = f"/v1/courses/{course_id}/syllabus"
    return response


# ─── GET /v1/courses/{course_id}/syllabus ───
@router.get("")
def get_syllabus(
    course_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    path = request.url.path
    course, err = get_course_or_error(course_id, db, path)
    if err:
        return err

    syllabus = db.query(Syllabus).filter(Syllabus.course_id == course_id).first()
    if not syllabus:
        return error_response(404, "Not Found", "No syllabus found for this course", path)

    return SyllabusResponse.model_validate(syllabus).model_dump(mode="json")


# ─── DELETE /v1/courses/{course_id}/syllabus ───
@router.delete("")
def delete_syllabus(
    course_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    path = request.url.path
    course, err = get_course_or_error(course_id, db, path)
    if err:
        return err

    syllabus = db.query(Syllabus).filter(Syllabus.course_id == course_id).first()
    if not syllabus:
        return error_response(404, "Not Found", "No syllabus found for this course", path)

    # Delete from S3
    try:
        delete_file_from_s3(syllabus.s3_bucket_name, syllabus.s3_object_key)
    except Exception as e:
        return error_response(500, "Internal Server Error", f"Failed to delete file from S3: {str(e)}", path)

    # Delete metadata from DB
    db.delete(syllabus)

    # Update course flag
    course.has_syllabus = False
    course.date_updated = datetime.now(timezone.utc)

    db.commit()
    return JSONResponse(status_code=204, content=None)