from fastapi.responses import JSONResponse
from datetime import datetime, timezone


def error_response(status_code: int, error: str, message: str, path: str) -> JSONResponse:
    """
    Return a JSON error response matching the Swagger Error schema:
    {
        "error": "...",
        "message": "...",
        "timestamp": "...",
        "path": "..."
    }
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": path,
        },
    )