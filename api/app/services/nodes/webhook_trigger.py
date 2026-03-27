from __future__ import annotations
from app.services.nodes.base import NodeContext, NodeResult, NodeDefinition, simple_schema


def execute(ctx: NodeContext) -> NodeResult:
    payload = ctx.trigger_payload or {}
    return NodeResult(output=payload, logs=[f"webhook trigger with {len(payload)} keys"])


definition = NodeDefinition(
    type="webhook_trigger",
    name="Webhook Trigger",
    category="trigger",
    description="Starts a workflow when an HTTP webhook fires.",
    schema=simple_schema(
        {
            "path": {"type": "string", "description": "Public path segment /api/webhooks/{path}"},
            "verify_signature": {"type": "boolean", "default": True},
        }
    ),
    execute=execute,
)
