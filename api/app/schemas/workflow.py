from __future__ import annotations
from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator


class NodePosition(BaseModel):
    x: float = 0
    y: float = 0


class WorkflowNode(BaseModel):
    id: str
    type: str  # e.g. "http_request", "hubspot_create_contact"
    label: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    position: NodePosition = Field(default_factory=NodePosition)


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    source_handle: str | None = None
    target_handle: str | None = None


class WorkflowGraph(BaseModel):
    nodes: list[WorkflowNode] = Field(default_factory=list)
    edges: list[WorkflowEdge] = Field(default_factory=list)

    @field_validator("nodes")
    @classmethod
    def unique_node_ids(cls, v: list[WorkflowNode]) -> list[WorkflowNode]:
        ids = [n.id for n in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate node ids")
        return v


class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    graph: WorkflowGraph = Field(default_factory=WorkflowGraph)
    is_active: bool = True


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    graph: WorkflowGraph | None = None
    is_active: bool | None = None


class WorkflowRead(BaseModel):
    id: str
    name: str
    description: str | None
    graph: WorkflowGraph
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RunRead(BaseModel):
    id: str
    workflow_id: str
    status: Literal["pending", "running", "success", "failed"]
    trigger_payload: dict | None
    node_logs: list[dict]
    error: str | None
    started_at: datetime
    finished_at: datetime | None

    model_config = {"from_attributes": True}


class RunCreate(BaseModel):
    payload: dict[str, Any] | None = None
