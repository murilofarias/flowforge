from __future__ import annotations
import time
from app.services.nodes.base import NodeContext, NodeResult, NodeDefinition, simple_schema


def execute(ctx: NodeContext) -> NodeResult:
    seconds = float(ctx.config.get("seconds", 0))
    if ctx.fixture_mode:
        seconds = min(seconds, 0.01)
    if seconds > 0:
        time.sleep(seconds)
    return NodeResult(output={"waited": seconds}, logs=[f"delay {seconds}s"])


definition = NodeDefinition(
    type="delay",
    name="Delay",
    category="logic",
    description="Pause execution for N seconds.",
    schema=simple_schema({"seconds": {"type": "number", "default": 1}}),
    execute=execute,
)
