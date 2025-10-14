import anyio
from app.utils.databases import create_postgres, create_redis, create_timescaledb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session


async def lifespan(app: FastAPI):
    app.state.postgres = create_postgres()
    app.state.timescaledb = create_timescaledb()
    app.state.redis = create_redis()

    yield
    await app.state.postgres.dispose()
    await app.state.timescaledb.dispose()
    await app.state.redis.close()


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
def ping():
    return {"ok": True}
