from typing import Annotated, AsyncGenerator, Literal, Optional

import anyio
import app.models
from app.models.device import Device
from app.utils.databases import create_postgres, create_redis, create_timescaledb
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def lifespan(app: FastAPI):
    # Database engines
    app.state.postgres = create_postgres()
    app.state.timescaledb = create_timescaledb()
    app.state.redis = create_redis()

    # Session constructor
    app.state.sessions = {
        "pg": async_sessionmaker(
            app.state.postgres, expire_on_commit=False, class_=AsyncSession
        ),
        "ts": async_sessionmaker(
            app.state.timescaledb, expire_on_commit=False, class_=AsyncSession
        ),
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


class DevicePut(BaseModel):
    name: str
    ip_address: str
    device_type: str
    vendor: str
    model: str
    os_version: str
    location: str
    is_active: bool
    snmp_config: Optional[str] = None
    ssh_config: Optional[str] = None
    api_config: Optional[str] = None


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
async def get_all_devices(session: SessionPG):  # type: ignore
    devices = (await session.execute(select(Device))).scalars().all()
    return [{"id": d.id, "name": d.name, "ip_address": d.ip_address} for d in devices]


@app.get("/api/v1/devices/{id}")
async def get_device(id: int, session: SessionPG):
    device = (
        (await session.execute(select(Device).where(Device.id == id))).scalars().all()
    )
    return [{"id": d.id, "name": d.name, "ip_address": d.ip_address} for d in device]


@app.delete("/api/v1/devices/{id}")
async def delete_device(id: int, session: SessionPG):
    device = await session.get(Device, id)
    await session.delete(device)
    await session.commit()
    return Response(status_code=200)


@app.post("/api/v1/devices")
async def add_device(payload: DevicePut, session: SessionPG):

    exists_q = await session.execute(
        select(Device).where(Device.ip_address == payload.ip_address)
    )
    if exists_q.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="device with this ip_address already exists"
        )

    device = Device(**payload.model_dump())

    session.add(device)
    await session.commit()
    await session.refresh(device)

    return {"id": device.id, "name": device.name}


@app.put("/api/v1/devices/{id}")
async def edit_device(id: int, payload: DevicePut, session: SessionPG):
    device = await session.get(Device, id)
    if not device:
        raise HTTPException(404, "Device not found")

    exists_q = await session.execute(
        select(Device.id).where(
            Device.ip_address == payload.ip_address, Device.id != id
        )
    )
    if exists_q.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="device with this ip_address already exists"
        )

    for field, value in payload.model_dump().items():
        setattr(device, field, value)

    await session.commit()
    await session.refresh(device)

    return {"id": device.id, "name": device.name}
