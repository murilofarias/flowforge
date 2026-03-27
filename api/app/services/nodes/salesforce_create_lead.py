from __future__ import annotations
from app.services.nodes.base import NodeContext, NodeResult, NodeDefinition, simple_schema


def execute(ctx: NodeContext) -> NodeResult:
    email = ctx.config.get("email", "")
    company = ctx.config.get("company", "")
    if ctx.fixture_mode:
        return NodeResult(
            output={"lead_id": "sf_fixture_456", "email": email, "company": company, "created": True},
            logs=[f"[fixture] salesforce create lead {email}"],
        )
    return NodeResult(output={"lead_id": None, "created": False})


definition = NodeDefinition(
    type="salesforce_create_lead",
    name="Salesforce: Create Lead",
    category="action",
    description="Create a new lead in Salesforce.",
    schema=simple_schema(
        {
            "email": {"type": "string", "format": "email"},
            "company": {"type": "string"},
            "first_name": {"type": "string"},
            "last_name": {"type": "string"},
        },
        required=["email", "company"],
    ),
    execute=execute,
)
