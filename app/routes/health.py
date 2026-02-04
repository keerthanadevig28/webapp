from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import HealthCheck

router = APIRouter()

@router.get("/healthz", status_code=status.HTTP_200_OK)
async def health_check(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Health check endpoint - checks database connectivity.
    
    Requirements:
    - Only GET method supported (405 for others)
    - No payload allowed (400 if payload present)
    - No query parameters allowed (400 if present)
    - Empty response body
    - Cache-Control: no-cache header
    - Insert record into health_checks table
    - Return 200 if successful, 503 if database fails
    """
    
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "X-Content-Type-Options": "nosniff"
    }
    
    if request.query_params:
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=headers
        )
    
    body = await request.body()
    if body:
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=headers
        )

    try:

        db.execute(text("SELECT 1"))
        
        health_check_record = HealthCheck()
        db.add(health_check_record)
        db.commit()
        
        return Response(
            status_code=status.HTTP_200_OK,
            headers=headers
        )
        
    except Exception as e:
        print(f"Health check failed: {e}")
        db.rollback()
        
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            headers=headers
        )

@router.head("/healthz")
@router.post("/healthz")
@router.put("/healthz")
@router.patch("/healthz")
@router.delete("/healthz")
async def health_check_not_allowed():
    """Return 405 for non-GET methods with required headers"""
    return Response(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "X-Content-Type-Options": "nosniff"
        }
    )