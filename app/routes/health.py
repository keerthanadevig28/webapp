from fastapi import APIRouter, Request, Response, HTTPException
from app.config import get_settings
import psycopg2

router = APIRouter()

@router.get("/healthz")
async def health_check(request: Request):
    """Health check with direct psycopg2 connection"""
    body = await request.body()
    if body:
        raise HTTPException(status_code=400)
    
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "X-Content-Type-Options": "nosniff"
    }
    
    settings = get_settings()
    
    print(f"DEBUG: Attempting to connect to database at {settings.db_host}:{settings.db_port}")
    
    try:
        # Direct psycopg2 connection - no pooling
        conn = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            connect_timeout=2
        )
        
        print("DEBUG: Database connection successful")
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO health_checks (check_datetime) VALUES (NOW())")
        conn.commit()
        cursor.close()
        conn.close()
        
        return Response(status_code=200, headers=headers)
    
    except Exception as e:
        print(f"DEBUG: Database error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=503)

@router.post("/healthz")
@router.put("/healthz")
@router.delete("/healthz")
@router.patch("/healthz")
@router.head("/healthz")
async def method_not_allowed():
    raise HTTPException(status_code=405)
