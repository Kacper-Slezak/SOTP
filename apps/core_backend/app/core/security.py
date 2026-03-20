import passlib.hash


def hash_password(password: str) -> str:
    # Placeholder for password hashing logic
    return passlib.hash.bcrypt.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    # Placeholder for password verification logic
    return passlib.hash.bcrypt.verify(password, hashed_password)


def create_access_token(data: dict) -> str:
    # Placeholder for token creation logic
    return "fake-jwt-token"


def decode_access_token(token: str) -> dict:
    # Placeholder for token decoding logic
    return {"user_id": 1}
