from __future__ import annotations
import httpx
from app.services.nodes.base import NodeContext, NodeResult, NodeDefinition, simple_schema


def execute(ctx: NodeContext) -> NodeResult:
    method = ctx.config.get("method", "GET").upper()
    url = ctx.config.get("url", "")
    headers = ctx.config.get("headers", {}) or {}
    body = ctx.config.get("body")

    if ctx.fixture_mode or not url:
        return NodeResult(
            output={"status": 200, "body": {"ok": True, "fixture": True, "url": url}},
            logs=[f"[fixture] {method} {url}"],
        )

    with httpx.Client(timeout=15) as client:
        resp = client.request(method, url, headers=headers, json=body)
    out = {"status": resp.status_code, "body": _safe_json(resp)}
    return NodeResult(output=out, logs=[f"{method} {url} -> {resp.status_code}"])


def _safe_json(resp: httpx.Response):
    try:
        return resp.json()
    except Exception:
        return {"text": resp.text[:2000]}


definition = NodeDefinition(
    type="http_request",
    name="HTTP Request",
    category="action",
    description="Make an HTTP request to any URL.",
    schema=simple_schema(
        {
            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"], "default": "GET"},
            "url": {"type": "string", "title": "URL"},
            "headers": {"type": "object", "additionalProperties": {"type": "string"}},
            "body": {"type": "object"},
        },
        required=["url"],
    ),
    execute=execute,
)
