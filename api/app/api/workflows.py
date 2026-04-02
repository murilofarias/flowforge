from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models import Workflow, Run
from app.schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowRead, RunCreate, RunRead,
)
from app.celery_client import enqueue_run

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.get("", response_model=list[WorkflowRead])
def list_workflows(db: Session = Depends(get_db)) -> list[WorkflowRead]:
    rows = db.execute(select(Workflow).order_by(Workflow.updated_at.desc())).scalars().all()
    return [WorkflowRead.model_validate(r) for r in rows]


@router.post("", response_model=WorkflowRead, status_code=status.HTTP_201_CREATED)
def create_workflow(data: WorkflowCreate, db: Session = Depends(get_db)) -> WorkflowRead:
    wf = Workflow(
        name=data.name,
        description=data.description,
        graph=data.graph.model_dump(),
        is_active=data.is_active,
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return WorkflowRead.model_validate(wf)


@router.get("/{workflow_id}", response_model=WorkflowRead)
def get_workflow(workflow_id: str, db: Session = Depends(get_db)) -> WorkflowRead:
    wf = db.get(Workflow, workflow_id)
    if not wf:
        raise HTTPException(404, "Workflow not found")
    return WorkflowRead.model_validate(wf)


@router.patch("/{workflow_id}", response_model=WorkflowRead)
def update_workflow(workflow_id: str, data: WorkflowUpdate, db: Session = Depends(get_db)) -> WorkflowRead:
    wf = db.get(Workflow, workflow_id)
    if not wf:
        raise HTTPException(404, "Workflow not found")
    if data.name is not None:
        wf.name = data.name
    if data.description is not None:
        wf.description = data.description
    if data.graph is not None:
        wf.graph = data.graph.model_dump()
    if data.is_active is not None:
        wf.is_active = data.is_active
    db.commit()
    db.refresh(wf)
    return WorkflowRead.model_validate(wf)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(workflow_id: str, db: Session = Depends(get_db)) -> None:
    wf = db.get(Workflow, workflow_id)
    if not wf:
        raise HTTPException(404, "Workflow not found")
    db.delete(wf)
    db.commit()


@router.post("/{workflow_id}/run", response_model=RunRead, status_code=status.HTTP_202_ACCEPTED)
def run_workflow(workflow_id: str, body: RunCreate | None = None, db: Session = Depends(get_db)) -> RunRead:
    wf = db.get(Workflow, workflow_id)
    if not wf:
        raise HTTPException(404, "Workflow not found")
    run = Run(workflow_id=workflow_id, status="pending", trigger_payload=(body.payload if body else None))
    db.add(run)
    db.commit()
    db.refresh(run)
    try:
        enqueue_run(run.id)
    except Exception:
        # Fall back to sync execution if broker unreachable (dev convenience).
        from app.services.workflow import run_workflow as sync_run
        sync_run(db, run.id)
        db.refresh(run)
    return RunRead.model_validate(run)
