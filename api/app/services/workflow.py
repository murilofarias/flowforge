"""Workflow graph resolution and execution engine."""
from __future__ import annotations
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Workflow, Run
from app.services.nodes import get_node
from app.services.nodes.base import NodeContext


class GraphError(Exception):
    pass


def topological_order(nodes: list[dict], edges: list[dict]) -> list[str]:
    ids = {n["id"] for n in nodes}
    indeg: dict[str, int] = {i: 0 for i in ids}
    adj: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        s, t = e["source"], e["target"]
        if s not in ids or t not in ids:
            raise GraphError(f"Edge references unknown node: {s}->{t}")
        adj[s].append(t)
        indeg[t] += 1

    queue: deque[str] = deque([i for i, d in indeg.items() if d == 0])
    order: list[str] = []
    while queue:
        nid = queue.popleft()
        order.append(nid)
        for nxt in adj[nid]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)
    if len(order) != len(ids):
        raise GraphError("Cycle detected in workflow graph")
    return order


def _incoming_edges(edges: list[dict], node_id: str) -> list[dict]:
    return [e for e in edges if e["target"] == node_id]


def execute_graph(
    graph: dict,
    trigger_payload: dict | None = None,
    fixture_mode: bool | None = None,
) -> tuple[str, list[dict], dict[str, Any]]:
    """Pure execution: returns (status, logs, outputs_by_node)."""
    settings = get_settings()
    fm = settings.fixture_mode if fixture_mode is None else fixture_mode
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not nodes:
        return "success", [], {}

    order = topological_order(nodes, edges)
    node_by_id = {n["id"]: n for n in nodes}
    outputs: dict[str, Any] = {}
    skipped: set[str] = set()
    logs: list[dict] = []
    status = "success"

    for nid in order:
        node = node_by_id[nid]
        incoming = _incoming_edges(edges, nid)
        # Propagate skips: if any upstream is skipped AND produced a branch
        # that doesn't match this edge's source_handle, skip this node too.
        upstream_blocked = False
        for edge in incoming:
            src = edge["source"]
            if src in skipped:
                upstream_blocked = True
                break
        if upstream_blocked:
            skipped.add(nid)
            logs.append({
                "node_id": nid,
                "type": node["type"],
                "status": "skipped",
                "logs": ["skipped due to upstream filter"],
                "at": datetime.now(timezone.utc).isoformat(),
            })
            continue

        inputs = {e["source"]: outputs.get(e["source"]) for e in incoming}
        try:
            defn = get_node(node["type"])
        except KeyError as e:
            logs.append({
                "node_id": nid,
                "type": node["type"],
                "status": "failed",
                "error": str(e),
                "logs": [],
                "at": datetime.now(timezone.utc).isoformat(),
            })
            return "failed", logs, outputs

        ctx = NodeContext(
            node_id=nid,
            config=node.get("config", {}) or {},
            inputs=inputs,
            trigger_payload=trigger_payload,
            fixture_mode=fm,
        )
        started = datetime.now(timezone.utc).isoformat()
        try:
            result = defn.execute(ctx)
        except Exception as e:  # noqa: BLE001
            logs.append({
                "node_id": nid,
                "type": node["type"],
                "status": "failed",
                "error": f"{type(e).__name__}: {e}",
                "logs": [],
                "started_at": started,
                "at": datetime.now(timezone.utc).isoformat(),
            })
            return "failed", logs, outputs

        outputs[nid] = result.output
        if result.skipped:
            skipped.add(nid)
        logs.append({
            "node_id": nid,
            "type": node["type"],
            "status": "skipped" if result.skipped else "success",
            "input": inputs,
            "output": result.output,
            "branch": result.branch,
            "logs": result.logs,
            "started_at": started,
            "at": datetime.now(timezone.utc).isoformat(),
        })

    return status, logs, outputs


def run_workflow(db: Session, run_id: str) -> None:
    """Celery entrypoint — loads run + workflow, executes, persists results."""
    run = db.get(Run, run_id)
    if not run:
        raise ValueError(f"Run {run_id} not found")
    workflow = db.get(Workflow, run.workflow_id)
    if not workflow:
        run.status = "failed"
        run.error = "Workflow missing"
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
        return

    run.status = "running"
    db.commit()

    try:
        status, logs, _outputs = execute_graph(workflow.graph, run.trigger_payload)
        run.status = status
        run.node_logs = logs
    except Exception as e:  # noqa: BLE001
        run.status = "failed"
        run.error = f"{type(e).__name__}: {e}"
    finally:
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
