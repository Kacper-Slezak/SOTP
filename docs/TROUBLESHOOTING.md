# Troubleshooting Guide

This guide addresses common issues encountered during local development with Docker Compose.

## 1. Initial Setup and Dependencies

### Issue: `make dev` fails with "Service 'X' failed to build"

This typically indicates an issue during the Docker image build process.

**Solution:**
1.**Check Context:** Ensure you are in the project root directory (`/sotp`).
2.**Review Logs:** Run the build command explicitly to see the detailed error:
    *For Backend: `docker build ./backend`
    *For Frontend: `docker build ./frontend`
3.**Dependency Caching:** If dependencies were recently added, run `make down` to stop containers, then clean up old volumes with `make clean` and try `make dev` again.

### Issue: Frontend fails to start inside Docker with module errors

This is often caused by volume mounting issues in Next.js/Node.js environments.

**Solution:**
The `docker-compose.dev.yml` file is configured with external volumes for `/workspace/frontend/node_modules` and `/.next`. If you encounter errors, try:
1.**Clearing Cache:** Delete the local `frontend/node_modules` and `frontend/.next` folders.
2.**Rebuilding:** Run `make down` followed by `make dev`.

## 2. Database and Backend Connectivity

### Issue: Backend `backend` container keeps restarting or fails on startup

The backend runs Alembic migrations on startup.

**Solution:**
1.**Check Dependencies:** Run `make logs` and check for errors related to PostgreSQL, TimescaleDB, or Alembic.
2.**Verify DB Health:** Wait until the `postgres` and `timescale` services pass their health checks (indicated by `condition: service_healthy` in the compose file).
3.**Migration Errors:** If the error is `sqlalchemy.exc.ProgrammingError`, enter the backend container: `make shell-backend` and run the migrations manually:
    *`alembic -x db=postgres upgrade postgres@head`
    *`alembic -x db=timescale upgrade timescale@head`

### Issue: Frontend cannot connect to the API (CORS or 404/500 errors)

The frontend (`http://localhost:3000`) communicates with the backend (`http://localhost:8000`).

**Solution:**

1.**Verify Ports:** Ensure the backend container is running and accessible on port 8000: `curl http://localhost:8000/ping`. It should return `{"ok": true}`.
2.**Check Middleware:** Verify the `CORSMiddleware` configuration in `backend/app/main.py` is correctly configured to allow requests from the frontend origin. The current config allows `http://localhost`, `http://localhost:8080`, and regex-matching of local IPs.
