from fastapi import APIRouter, Request, Response, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.config import get_settings

router = APIRouter()

@router.get("/healthz")
async def health_check(request: Request):
    """Health check - tests database connectivity with fresh connection"""
    body = await request.body()
    if body:
        raise HTTPException(status_code=400)
    
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "X-Content-Type-Options": "nosniff"
    }
    
    try:
        # Create a fresh connection to test database availability
        settings = get_settings()
        test_engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,  # Test connection before using
            pool_size=1,
            max_overflow=0
        )
        
        # Try to execute a simple query
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
            # Insert health check record
            conn.execute(
                text("INSERT INTO health_checks (check_datetime) VALUES (NOW())")
            )
            conn.commit()
        
        test_engine.dispose()
        return Response(status_code=200, headers=headers)
    
    except OperationalError:
        # Database connection failed
        raise HTTPException(status_code=503)
    except Exception as e:
        # Any other database error
        raise HTTPException(status_code=503)

@router.post("/healthz")
@router.put("/healthz")
@router.delete("/healthz")
@router.patch("/healthz")
@router.head("/healthz")
async def method_not_allowed():
    raise HTTPException(status_code=405)
