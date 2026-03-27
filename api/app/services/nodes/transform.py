from __future__ import annotations
import ast
import operator as op
from typing import Any
from app.services.nodes.base import NodeContext, NodeResult, NodeDefinition, simple_schema


_SAFE_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Mod: op.mod, ast.Pow: op.pow, ast.USub: op.neg, ast.UAdd: op.pos,
    ast.Eq: op.eq, ast.NotEq: op.ne, ast.Lt: op.lt, ast.LtE: op.le,
    ast.Gt: op.gt, ast.GtE: op.ge, ast.And: lambda a, b: a and b, ast.Or: lambda a, b: a or b,
    ast.Not: op.not_,
}


def _eval(node: ast.AST, scope: dict[str, Any]) -> Any:
    if isinstance(node, ast.Expression):
        return _eval(node.body, scope)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in scope:
            return scope[node.id]
        raise ValueError(f"Unknown name: {node.id}")
    if isinstance(node, ast.BinOp):
        return _SAFE_OPS[type(node.op)](_eval(node.left, scope), _eval(node.right, scope))
    if isinstance(node, ast.UnaryOp):
        return _SAFE_OPS[type(node.op)](_eval(node.operand, scope))
    if isinstance(node, ast.BoolOp):
        values = [_eval(v, scope) for v in node.values]
        result = values[0]
        for v in values[1:]:
            result = _SAFE_OPS[type(node.op)](result, v)
        return result
    if isinstance(node, ast.Compare):
        left = _eval(node.left, scope)
        for opn, comparator in zip(node.ops, node.comparators):
            right = _eval(comparator, scope)
            if not _SAFE_OPS[type(opn)](left, right):
                return False
            left = right
        return True
    if isinstance(node, ast.Subscript):
        val = _eval(node.value, scope)
        key = _eval(node.slice, scope)
        return val[key]
    if isinstance(node, ast.Attribute):
        val = _eval(node.value, scope)
        if isinstance(val, dict):
            return val.get(node.attr)
        raise ValueError("Attribute access only allowed on dicts")
    if isinstance(node, ast.Dict):
        return {_eval(k, scope): _eval(v, scope) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.List):
        return [_eval(e, scope) for e in node.elts]
    raise ValueError(f"Disallowed expression: {type(node).__name__}")


def safe_eval(expr: str, scope: dict[str, Any]) -> Any:
    tree = ast.parse(expr, mode="eval")
    return _eval(tree, scope)


def execute(ctx: NodeContext) -> NodeResult:
    mapping: dict[str, str] = ctx.config.get("mapping", {}) or {}
    scope = {"inputs": ctx.inputs, "trigger": ctx.trigger_payload or {}}
    output: dict[str, Any] = {}
    for k, expr in mapping.items():
        try:
            output[k] = safe_eval(expr, scope)
        except Exception as e:
            output[k] = None
            return NodeResult(output=output, logs=[f"transform error on '{k}': {e}"])
    return NodeResult(output=output, logs=[f"transform produced {len(output)} keys"])


definition = NodeDefinition(
    type="transform",
    name="Transform",
    category="transform",
    description="Map/compute new fields using safe expressions. Available scope: inputs, trigger.",
    schema=simple_schema(
        {
            "mapping": {
                "type": "object",
                "title": "Mapping (key -> expression)",
                "additionalProperties": {"type": "string"},
            }
        }
    ),
    execute=execute,
)
