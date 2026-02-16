from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.database import init_db
from app.routes import health, user
from app.config import get_settings
from fastapi.exceptions import RequestValidationError
from app.routes.metadata import router as metadata_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
  
    init_db()
    print(f"Application started on {settings.app_host}:{settings.app_port}")
    yield
    
    print("Application shutting down")


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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully"""
    print(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert 422 validation errors to 400 Bad Request"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Bad Request"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True  
    )

    