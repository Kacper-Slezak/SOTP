from datetime import datetime, timedelta, timezone

import jose
import passlib.hash
from app.core.config import Config

SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = Config.REFRESH_TOKEN_EXPIRE_DAYS


def hash_password(password: str) -> str:
    """Hash the password using bcrypt algorithm."""
    return passlib.hash.bcrypt.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify the password against the hashed password."""
    return passlib.hash.bcrypt.verify(password, hashed_password)


def create_access_token(data: dict) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = data.copy()
    payload.update({"exp": exp, "type": "access"})

    return jose.jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode a JWT token and return the payload."""
    try:
        payload = jose.jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jose.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jose.JWTError:
        raise ValueError("Invalid token")


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with a longer expiration time."""
    exp = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = data.copy()
    payload.update({"exp": exp, "type": "refresh"})

    return jose.jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
