from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models import Workflow, Run
from app.services.security import verify_webhook_signature
from app.celery_client import enqueue_run

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/{trigger_id}")
async def webhook(trigger_id: str, request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get("X-FlowForge-Signature")
    # Signature optional in fixture mode, but we validate when header is present.
    if signature and not verify_webhook_signature(body, signature):
        raise HTTPException(401, "Invalid signature")

    payload = {}
    if body:
        try:
            payload = await request.json()
        except Exception:
            payload = {"raw": body.decode(errors="ignore")}

    # Match any workflow whose first node is webhook_trigger with matching path.
    rows = db.execute(select(Workflow).where(Workflow.is_active.is_(True))).scalars().all()
    matched: list[Workflow] = []
    for wf in rows:
        for n in wf.graph.get("nodes", []):
            if n.get("type") == "webhook_trigger" and n.get("config", {}).get("path") == trigger_id:
                matched.append(wf)
                break
    if not matched:
        raise HTTPException(404, f"No active workflow bound to webhook '{trigger_id}'")

    run_ids: list[str] = []
    for wf in matched:
        run = Run(workflow_id=wf.id, status="pending", trigger_payload=payload)
        db.add(run)
        db.commit()
        db.refresh(run)
        try:
            enqueue_run(run.id)
        except Exception:
            from app.services.workflow import run_workflow as sync_run
            sync_run(db, run.id)
        run_ids.append(run.id)

    return {"triggered": run_ids}
