from __future__ import annotations
from app.services.nodes.base import NodeContext, NodeResult, NodeDefinition, simple_schema
from app.services.nodes.transform import safe_eval


def execute(ctx: NodeContext) -> NodeResult:
    expr = ctx.config.get("condition", "True")
    scope = {"inputs": ctx.inputs, "trigger": ctx.trigger_payload or {}}
    try:
        passed = bool(safe_eval(expr, scope))
    except Exception as e:
        return NodeResult(output={"passed": False, "error": str(e)}, skipped=True, logs=[f"filter error: {e}"])
    return NodeResult(
        output={"passed": passed},
        skipped=not passed,
        branch="true" if passed else "false",
        logs=[f"filter {expr!r} -> {passed}"],
    )


definition = NodeDefinition(
    type="filter",
    name="Filter",
    category="logic",
    description="Short-circuit downstream nodes unless condition passes.",
    schema=simple_schema(
        {"condition": {"type": "string", "default": "True"}},
        required=["condition"],
    ),
    execute=execute,
)
