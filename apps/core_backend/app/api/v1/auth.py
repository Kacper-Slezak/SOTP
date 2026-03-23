from app.api.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.deps import SessionPG
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
async def login(payload: LoginRequest, session: SessionPG):
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/register", status_code=201)
async def register(payload: RegisterRequest, session: SessionPG):
    result = await session.execute(select(User).where(User.email == payload.email))
    email_exists = result.scalar_one_or_none()
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    hashed_password = hash_password(payload.password)
    new_user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hashed_password,
        role=UserRole.READONLY,
        is_active=True,
    )
    session.add(new_user)
    await session.commit()

    return {"message": "Registration successful"}


@router.post("/refresh")
async def refresh(payload: RefreshRequest, session: SessionPG):
    try:
        token_data = decode_access_token(payload.refresh_token)
        user_id = token_data.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    user = await session.get(User, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    if token_data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    new_access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return {"access_token": new_access_token, "token_type": "bearer"}
