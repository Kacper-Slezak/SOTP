from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str
