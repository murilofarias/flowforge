from __future__ import annotations
from app.services.nodes.base import NodeContext, NodeResult, NodeDefinition, simple_schema


def execute(ctx: NodeContext) -> NodeResult:
    deal_id = ctx.config.get("deal_id", "")
    stage = ctx.config.get("stage", "")
    amount = ctx.config.get("amount")
    if ctx.fixture_mode:
        return NodeResult(
            output={"deal_id": deal_id, "stage": stage, "amount": amount, "updated": True},
            logs=[f"[fixture] hubspot update deal {deal_id} -> {stage}"],
        )
    return NodeResult(output={"deal_id": deal_id, "updated": False})


definition = NodeDefinition(
    type="hubspot_update_deal",
    name="HubSpot: Update Deal",
    category="action",
    description="Update an existing HubSpot deal.",
    schema=simple_schema(
        {
            "deal_id": {"type": "string"},
            "stage": {"type": "string"},
            "amount": {"type": "number"},
        },
        required=["deal_id"],
    ),
    execute=execute,
)
