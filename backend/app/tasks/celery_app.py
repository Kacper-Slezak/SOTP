# backend/app/tasks/celery_app.py
from celery import Celery
from app.core.config import Config # Import Config

# Use the Redis URL from the configuration
redis_url = Config.REDIS_URL

celery_app = Celery(
    "sotp_tasks",
    broker=redis_url,
    backend=redis_url,
    include=["app.tasks.monitoring_tasks"], 
)

celery_app.conf.update(
    task_track_started=True,
)