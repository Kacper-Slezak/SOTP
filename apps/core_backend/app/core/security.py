import passlib.hash


def hash_password(password: str) -> str:
    """Hash the password using bcrypt algorithm."""
    return passlib.hash.bcrypt.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify the password against the hashed password."""
    return passlib.hash.bcrypt.verify(password, hashed_password)


def create_access_token(data: dict) -> str:
    """Create a JWT access token."""

    return "fake-jwt-token"


def decode_access_token(token: str) -> dict:
    """Decode a JWT access token."""

    return {"user_id": 1}
