from fastapi import APIRouter, Request, Response
from app.config import get_settings
from app.logger import logger
from app.metrics import count, timed
import psycopg2

router = APIRouter()


@router.get("/healthz")
async def health_check(request: Request):
    count("api.healthz")
    logger.info("GET /healthz called")

    body = await request.body()
    if body:
        logger.warning("Health check failed — request body not allowed")
        return Response(status_code=400)

    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "X-Content-Type-Options": "nosniff"
    }

    settings = get_settings()

    try:
        with timed("api.healthz.time"):
            with timed("db.health_check"):
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

        logger.info("Health check passed — database connection successful")
        return Response(status_code=200, headers=headers)

    except Exception as e:
        logger.error("Health check failed — database connection error",
                     extra={"error": str(e)}, exc_info=True)
        return Response(status_code=503)
@router.get("/healthz123")
async def health_check_123(request: Request):
    count("api.healthz123")
    logger.info("GET /healthz123 called")
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
        with timed("api.healthz123.time"):
            with timed("db.health_check"):
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
    except Exception as e:
        logger.error("Health check 123 failed", extra={"error": str(e)}, exc_info=True)
        return Response(status_code=503)

@router.post("/healthz")
@router.put("/healthz")
@router.delete("/healthz")
@router.patch("/healthz")
@router.head("/healthz")
async def method_not_allowed():
    logger.warning("Method not allowed on /healthz")
    return Response(status_code=405)
