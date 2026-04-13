"""Celery client used by the API to enqueue tasks (no task definitions live here)."""
from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery = Celery("flowforge", broker=settings.redis_url, backend=settings.redis_url)
celery.conf.task_default_queue = "flowforge"


def enqueue_run(run_id: str) -> None:
    celery.send_task("flowforge.execute_workflow", args=[run_id])
