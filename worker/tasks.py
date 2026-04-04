"""Celery tasks — thin wrappers that delegate to shared app.services code."""
from __future__ import annotations
from celery_app import celery
from app.db.session import session_scope
from app.services.workflow import run_workflow


@celery.task(name="flowforge.execute_workflow", bind=True, max_retries=0)
def execute_workflow(self, run_id: str) -> str:
    db = session_scope()
    try:
        run_workflow(db, run_id)
    finally:
        db.close()
    return run_id
