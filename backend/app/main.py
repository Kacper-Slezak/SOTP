import anyio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.utils.databases import create_postgres, create_timescaledb, create_redis

async def lifespan(app: FastAPI):
    app.state.postgres = create_postgres()
    app.state.timescaledb = create_timescaledb()
    app.state.redis = create_redis()

    yield
    app.state.postgres.dispose()
    app.state.timescaledb.dispose()
    await app.state.redis.close()


app = FastAPI(lifespan=lifespan)

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
async def main():
    def _pg():
        with app.state.postgres.connect() as c:
            return c.execute(text("SELECT 1")).scalar_one()

    def _ts():
        with app.state.timescaledb.connect() as c:
            return c.execute(text("SELECT 1")).scalar_one()

    pg_ok = await anyio.to_thread.run_sync(_pg)
    ts_ok = await anyio.to_thread.run_sync(_ts)
    redis_ok = await app.state.redis.ping()
    return {"status": "ok", "postgres": pg_ok, "timescaledb": ts_ok, "redis": redis_ok}