from app.api.dependencies import get_current_user
from app.api.v1.auth import router as auth_router
from app.api.v1.devices import router as devices_router
from app.api.v1.users import router as users_router
from app.utils.databases import create_postgres, create_redis, create_timescaledb
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
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


app = FastAPI(lifespan=lifespan, debug=True)
Instrumentator().instrument(app).expose(app)

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

app.include_router(auth_router)
app.include_router(devices_router, dependencies=[Depends(get_current_user)])
app.include_router(users_router)


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
