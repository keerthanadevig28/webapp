from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.cloud_metadata import CloudMetadataService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the cloud metadata service once at module load
cloud_service = CloudMetadataService()


@router.api_route("/v1/metadata", methods=["GET"], status_code=200)
async def get_metadata(request: Request):
    """
    Public endpoint to retrieve instance metadata from cloud platform
    No authentication required
    """
    # Check for request body - should not be present
    body = await request.body()
    if body:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Bad Request",
                "message": "Request body is not allowed for this endpoint"
            },
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache"
            }
        )
    
    # Check for query parameters - should not be present
    if request.query_params:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Bad Request",
                "message": "Query parameters are not allowed for this endpoint"
            },
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache"
            }
        )
    
    # Check if running on a supported cloud platform
    if not cloud_service.is_cloud_platform_detected():
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service Unavailable",
                "message": "Not running on a supported cloud platform (AWS or GCP)"
            },
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache"
            }
        )
    
    try:
        # Get metadata from the detected cloud platform
        metadata = cloud_service.get_metadata()
        
        # Create response with cache control headers
        return JSONResponse(
            content=metadata,
            status_code=200,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache"
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving metadata: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service Unavailable",
                "message": "Failed to retrieve instance metadata from cloud platform"
            },
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache"
            }
        )


@router.api_route("/v1/metadata", methods=["POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"], status_code=405)
async def metadata_method_not_allowed():
    """Handle all non-GET methods"""
    return JSONResponse(
        status_code=405,
        content={
            "error": "Method Not Allowed",
            "message": "Only GET method is allowed for this endpoint"
        },
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        }
    )