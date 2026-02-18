# backend/app/tasks/celery_app.py
from app.core.config import Config  # Import Config
from celery import Celery

# Use the Redis URL from the configuration
redis_url = Config.REDIS_URL

celery_app = Celery(
    "sotp_tasks",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    task_track_started=True,
)
