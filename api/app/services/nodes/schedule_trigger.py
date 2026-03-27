from __future__ import annotations
from app.services.nodes.base import NodeContext, NodeResult, NodeDefinition, simple_schema


def execute(ctx: NodeContext) -> NodeResult:
    return NodeResult(
        output={"triggered_at": ctx.trigger_payload.get("triggered_at") if ctx.trigger_payload else None},
        logs=["schedule trigger fired"],
    )


definition = NodeDefinition(
    type="schedule_trigger",
    name="Schedule Trigger",
    category="trigger",
    description="Starts a workflow on a cron schedule.",
    schema=simple_schema(
        {"cron": {"type": "string", "default": "0 * * * *", "description": "Cron expression"}},
        required=["cron"],
    ),
    execute=execute,
)
