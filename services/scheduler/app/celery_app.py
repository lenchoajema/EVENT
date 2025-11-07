from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

celery_app = Celery(
    "event_scheduler",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "monitor-uavs": {
            "task": "app.tasks.monitor_uav_status",
            "schedule": 30.0,  # every 30 seconds
        },
        "process-alerts": {
            "task": "app.tasks.process_pending_alerts",
            "schedule": 60.0,  # every 60 seconds
        },
    }
)
