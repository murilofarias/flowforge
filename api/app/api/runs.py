from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models import Run
from app.schemas.workflow import RunRead

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.get("", response_model=list[RunRead])
def list_runs(
    workflow_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
) -> list[RunRead]:
    q = select(Run).order_by(Run.started_at.desc()).limit(limit)
    if workflow_id:
        q = q.where(Run.workflow_id == workflow_id)
    if status:
        q = q.where(Run.status == status)
    return [RunRead.model_validate(r) for r in db.execute(q).scalars().all()]


@router.get("/{run_id}", response_model=RunRead)
def get_run(run_id: str, db: Session = Depends(get_db)) -> RunRead:
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return RunRead.model_validate(run)
