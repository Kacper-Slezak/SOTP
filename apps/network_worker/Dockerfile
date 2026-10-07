# Stage 1: Build with full dependencies
FROM python:3.11-slim as builder
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Final lightweight image
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl iproute2 grep postgresql-client git && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache /wheels/*
COPY . .
# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
