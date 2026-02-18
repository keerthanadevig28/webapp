from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.cloud_metadata import CloudMetadataService
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

cloud_service = CloudMetadataService()

CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache"
}

def error_response(status_code: int, error: str, message: str, path: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": path
        },
        headers=CACHE_HEADERS
    )


@router.api_route("/v1/metadata", methods=["GET"], status_code=200)
async def get_metadata(request: Request):
    """
    Public endpoint to retrieve instance metadata from cloud platform.
    No authentication required.
    """
    path = "/v1/metadata"

    body = await request.body()
    if body:
        return error_response(400, "Bad Request", "Request body is not allowed for this endpoint", path)

    if request.query_params:
        return error_response(400, "Bad Request", "Query parameters are not allowed for this endpoint", path)

    if not cloud_service.is_cloud_platform_detected():
        return error_response(503, "Service Unavailable", "Not running on a supported cloud platform (AWS or GCP)", path)

    try:
        metadata = cloud_service.get_metadata()
        return JSONResponse(
            content=metadata,
            status_code=200,
            headers=CACHE_HEADERS
        )
    except Exception as e:
        logger.error(f"Error retrieving metadata: {e}")
        return error_response(503, "Service Unavailable", "Failed to retrieve instance metadata from cloud platform", path)


@router.api_route("/v1/metadata", methods=["POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"], status_code=405)
async def metadata_method_not_allowed(request: Request):
    """Handle all non-GET methods"""
    return JSONResponse(
        status_code=405,
        content={
            "error": "Method Not Allowed",
            "message": "Only GET method is allowed for this endpoint",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": "/v1/metadata"
        },
        headers=CACHE_HEADERS
    )