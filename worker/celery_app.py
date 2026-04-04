"""Celery entrypoint — shares domain services with the API through /shared."""
from __future__ import annotations
import os
import sys

# /shared is the mounted api/ directory; ensure the `app` package is importable.
SHARED = os.environ.get("FLOWFORGE_SHARED", "/shared")
if SHARED not in sys.path:
    sys.path.insert(0, SHARED)

from celery import Celery  # noqa: E402
from app.core.config import get_settings  # noqa: E402

settings = get_settings()

celery = Celery(
    "flowforge",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["tasks"],
)
celery.conf.task_default_queue = "flowforge"
celery.conf.task_acks_late = True
celery.conf.worker_prefetch_multiplier = 1
