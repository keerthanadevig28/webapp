from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.database import init_db
from app.routes import health, user
from app.routes.metadata import router as metadata_router
from app.routes.course import router as course_router
from app.routes.syllabus import router as syllabus_router
from app.config import get_settings
from app.errors import error_response
from app.auth import AuthError
from app.logger import logger
from fastapi.exceptions import RequestValidationError

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed", extra={"error": str(e)}, exc_info=True)
    logger.info("Application started", extra={"host": settings.app_host, "port": settings.app_port})
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Cloud-Native Web Application",
    description="Backend API for user management with health monitoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.include_router(health.router, tags=["Health"])
app.include_router(user.router, tags=["User"])
app.include_router(metadata_router, tags=["Metadata"])
app.include_router(course_router)
app.include_router(syllabus_router)


@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    """Handle custom auth errors — returns the pre-built JSONResponse."""
    logger.warning("Authentication error", extra={"path": request.url.path})
    return exc.response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unexpected error", extra={"path": request.url.path, "error": str(exc)}, exc_info=True)
    return error_response(500, "Internal Server Error", "An unexpected error occurred", request.url.path)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Request validation failed", extra={"path": request.url.path, "error": str(exc)})
    return error_response(400, "Bad Request", "Request validation failed", request.url.path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
