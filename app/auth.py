import bcrypt
import base64
from fastapi import Depends, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.errors import error_response


class AuthError(Exception):
    """Custom exception that carries a JSONResponse."""
    def __init__(self, response: JSONResponse):
        self.response = response


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def decode_basic_auth(authorization: str) -> tuple:
    try:
        encoded = authorization.replace('Basic ', '')
        decoded = base64.b64decode(encoded).decode('utf-8')
        email, password = decoded.split(':', 1)
        return email, password
    except Exception:
        return None, None


def get_current_user(
    request: Request,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency: authenticate via Basic Auth, then check verified status.
    Returns the authenticated, verified user.
    """
    path = request.url.path

    if not authorization or not authorization.startswith('Basic '):
        raise AuthError(
            JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Authentication credentials are missing or invalid",
                    "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
                    "path": path,
                },
                headers={"WWW-Authenticate": "Basic"},
            )
        )

    email, password = decode_basic_auth(authorization)

    if not email or not password:
        raise AuthError(
            JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid authentication credentials",
                    "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
                    "path": path,
                },
                headers={"WWW-Authenticate": "Basic"},
            )
        )

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        raise AuthError(
            JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid credentials",
                    "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
                    "path": path,
                },
                headers={"WWW-Authenticate": "Basic"},
            )
        )

    # Check if account is verified
    if not user.verified:
        raise AuthError(
            error_response(403, "Forbidden", "Account not verified. Please verify your email first.", path)
        )

    return user