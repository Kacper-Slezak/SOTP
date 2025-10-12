# backend/app/tasks/celery_app.py
from celery import Celery

# TODO: W przyszłości załaduj konfigurację z pliku config.py
# Na razie wystarczą wartości na sztywno, aby usługa wstała.
redis_url = "redis://redis:6379/0"

celery_app = Celery(
    "sotp_tasks",
    broker=redis_url,
    backend=redis_url,
    include=["app.tasks.monitoring_tasks"], # Wskaż, gdzie będą Twoje zadania
)

celery_app.conf.update(
    task_track_started=True,
)