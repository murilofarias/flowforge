from __future__ import annotations
from app.services.nodes.base import NodeContext, NodeResult, NodeDefinition, simple_schema


def execute(ctx: NodeContext) -> NodeResult:
    channel = ctx.config.get("channel", "#general")
    text = ctx.config.get("text", "")
    if ctx.fixture_mode:
        return NodeResult(
            output={"channel": channel, "ts": "1700000000.000100", "sent": True},
            logs=[f"[fixture] slack -> {channel}: {text[:60]}"],
        )
    return NodeResult(output={"sent": False})


definition = NodeDefinition(
    type="slack_send_message",
    name="Slack: Send Message",
    category="action",
    description="Post a message to a Slack channel.",
    schema=simple_schema(
        {
            "channel": {"type": "string", "default": "#general"},
            "text": {"type": "string"},
        },
        required=["text"],
    ),
    execute=execute,
)
