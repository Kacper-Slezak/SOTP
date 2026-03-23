from app.api.dependencies import get_current_user
from app.models.user import User
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me")
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
