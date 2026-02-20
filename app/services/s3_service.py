import boto3
import uuid
from app.config import get_settings

settings = get_settings()

s3_client = boto3.client("s3", region_name=settings.aws_region)


def upload_file_to_s3(file_content: bytes, course_id: str, original_filename: str, content_type: str) -> dict:
    """
    Upload a file to S3 with collision-safe key:
      {course_id}/{uuid}/{original_filename}
    Returns dict with bucket_name, object_key, url, file_size.
    """
    bucket = settings.s3_bucket_name
    unique_id = str(uuid.uuid4())
    object_key = f"{course_id}/{unique_id}/{original_filename}"

    s3_client.put_object(
        Bucket=bucket,
        Key=object_key,
        Body=file_content,
        ContentType=content_type,
    )

    url = f"https://{bucket}.s3.{settings.aws_region}.amazonaws.com/{object_key}"

    return {
        "s3_bucket_name": bucket,
        "s3_object_key": object_key,
        "url": url,
        "file_size": len(file_content),
    }


def delete_file_from_s3(bucket_name: str, object_key: str):
    """Delete an object from S3."""
    s3_client.delete_object(Bucket=bucket_name, Key=object_key)