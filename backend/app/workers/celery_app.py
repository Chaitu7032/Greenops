from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "greenops_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Periodic schedule to poll for due deferred jobs every 60s
    beat_schedule={
        "check-due-deferred-jobs-every-minute": {
            "task": "app.workers.tasks.check_and_dispatch_deferred_jobs",
            "schedule": 60.0,
        },
    },
)
