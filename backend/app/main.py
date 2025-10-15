import anyio
import app.models
from app.utils.databases import create_postgres, create_redis, create_timescaledb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, Request
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import AsyncGenerator, Literal, Annotated
from app.models.device import Device

async def lifespan(app: FastAPI):
    #Database engines
    app.state.postgres = create_postgres()
    app.state.timescaledb = create_timescaledb()
    app.state.redis = create_redis()

    #Session constructor
    app.state.sessions = {
        "pg" : async_sessionmaker(app.state.postgres, expire_on_commit=False, class_=AsyncSession),
        "ts" : async_sessionmaker(app.state.timescaledb, expire_on_commit=False, class_=AsyncSession),
    }
    

    yield
    await app.state.postgres.dispose()
    await app.state.timescaledb.dispose()
    await app.state.redis.close()

def session_dep(which: Literal["pg", "ts"]):
    async def _get(request: Request):
        maker = request.app.state.sessions[which]
        async with maker() as session:
            yield session
    return _get

SessionPG = Annotated[AsyncSession, Depends(session_dep("pg"))]
SessionTS = Annotated[AsyncSession, Depends(session_dep("ts"))]

app = FastAPI(lifespan=lifespan, debug=True)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check databases
@app.get("/health")
async def health():
    errors = {}
    out = {}

    try:
        async with app.state.postgres.connect() as c:
            out["postgres"] = (await c.execute(text("SELECT 1"))).scalar_one()
    except Exception as e:
        errors["postgres"] = str(e)

    try:
        async with app.state.timescaledb.connect() as c:
            out["timescaledb"] = (await c.execute(text("SELECT 1"))).scalar_one()
    except Exception as e:
        errors["timescaledb"] = str(e)

    try:
        out["redis"] = bool(await app.state.redis.ping())
    except Exception as e:
        errors["redis"] = str(e)

    status = "ok" if not errors else "degraded"
    return {"status": status, "results": out, "errors": errors}


# Check app
@app.get("/ping")
async def ping():
    return {"ok": True}


@app.get("/api/v1/devices")
async def get_devices(session: SessionPG): # type: ignore
    rows = (await session.execute(select(Device))).scalars().all()
    return [{"id": d.id, "name": d.name} for d in rows]