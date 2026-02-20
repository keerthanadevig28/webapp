from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid import UUID

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Course, Syllabus
from app.schemas import SyllabusResponse
from app.services.s3_service import upload_file_to_s3, delete_file_from_s3

router = APIRouter(prefix="/v1/courses/{course_id}/syllabus", tags=["Syllabus"])


def get_course_or_404(course_id: UUID, db: Session) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


# ─── POST /v1/courses/{course_id}/syllabus ───
@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_syllabus(
    course_id: UUID,
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = get_course_or_404(course_id, db)

    # Check if syllabus already exists
    if course.has_syllabus:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A syllabus already exists for this course. Delete it first before uploading a new one."
        )

    # Validate file
    if file is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided. Use form field 'file'.")

    file_content = await file.read()

    if len(file_content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    # Upload to S3
    try:
        s3_result = upload_file_to_s3(
            file_content=file_content,
            course_id=str(course_id),
            original_filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to S3: {str(e)}"
        )

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
        status_code=status.HTTP_201_CREATED,
        content=SyllabusResponse.model_validate(syllabus).model_dump(mode="json"),
    )
    response.headers["Location"] = f"/v1/courses/{course_id}/syllabus"
    return response


# ─── GET /v1/courses/{course_id}/syllabus ───
@router.get("", response_model=SyllabusResponse)
def get_syllabus(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = get_course_or_404(course_id, db)

    syllabus = db.query(Syllabus).filter(Syllabus.course_id == course_id).first()
    if not syllabus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No syllabus found for this course"
        )

    return SyllabusResponse.model_validate(syllabus)


# ─── DELETE /v1/courses/{course_id}/syllabus ───
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_syllabus(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = get_course_or_404(course_id, db)

    syllabus = db.query(Syllabus).filter(Syllabus.course_id == course_id).first()
    if not syllabus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No syllabus found for this course"
        )

    # Delete from S3
    try:
        delete_file_from_s3(syllabus.s3_bucket_name, syllabus.s3_object_key)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file from S3: {str(e)}"
        )

    # Delete metadata from DB
    db.delete(syllabus)

    # Update course flag
    course.has_syllabus = False
    course.date_updated = datetime.now(timezone.utc)

    db.commit()
    return None