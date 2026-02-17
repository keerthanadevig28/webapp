from fastapi import APIRouter, Request, Response
from app.config import get_settings
import psycopg2

router = APIRouter()

@router.get("/healthz")
async def health_check(request: Request):
    body = await request.body()
    if body:
        return Response(status_code=400)

    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "X-Content-Type-Options": "nosniff"
    }

    settings = get_settings()

    try:
        conn = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            connect_timeout=2
        )

        cursor = conn.cursor()
        cursor.execute("INSERT INTO health_checks (check_datetime) VALUES (NOW())")
        conn.commit()
        cursor.close()
        conn.close()

        return Response(status_code=200, headers=headers)

    except Exception:
        return Response(status_code=503)


@router.post("/healthz")
@router.put("/healthz")
@router.delete("/healthz")
@router.patch("/healthz")
@router.head("/healthz")
async def method_not_allowed():
    return Response(status_code=405)
