from __future__ import annotations
from app.services.nodes.base import NodeContext, NodeResult, NodeDefinition, simple_schema


def execute(ctx: NodeContext) -> NodeResult:
    prompt = ctx.config.get("prompt", "")
    model = ctx.config.get("model", "gpt-4o-mini")
    if ctx.fixture_mode:
        canned = f"[fixture reply for '{prompt[:40]}...']"
        return NodeResult(
            output={"model": model, "content": canned, "tokens": 42},
            logs=[f"[fixture] openai:{model}"],
        )
    return NodeResult(output={"content": "", "tokens": 0})


definition = NodeDefinition(
    type="openai_chat",
    name="OpenAI: Chat",
    category="ai",
    description="Send a prompt to OpenAI chat completions.",
    schema=simple_schema(
        {
            "model": {"type": "string", "default": "gpt-4o-mini"},
            "prompt": {"type": "string"},
            "temperature": {"type": "number", "default": 0.7},
        },
        required=["prompt"],
    ),
    execute=execute,
)
