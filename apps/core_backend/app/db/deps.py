from typing import Annotated, Literal

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


def session_dep(which: Literal["pg", "ts"]):
    async def _get(request: Request):
        maker = request.app.state.sessions[which]
        async with maker() as session:
            yield session

    return _get


SessionPG = Annotated[AsyncSession, Depends(session_dep("pg"))]
SessionTS = Annotated[AsyncSession, Depends(session_dep("ts"))]
