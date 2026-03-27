from __future__ import annotations
from app.services.nodes.base import NodeContext, NodeResult, NodeDefinition, simple_schema


def execute(ctx: NodeContext) -> NodeResult:
    email = ctx.config.get("email", "")
    first = ctx.config.get("first_name", "")
    last = ctx.config.get("last_name", "")
    if ctx.fixture_mode:
        return NodeResult(
            output={"contact_id": "hs_fixture_123", "email": email, "created": True},
            logs=[f"[fixture] hubspot create contact {email}"],
        )
    # Real call would go here using hubspot_token.
    return NodeResult(output={"contact_id": None, "email": email, "created": False})


definition = NodeDefinition(
    type="hubspot_create_contact",
    name="HubSpot: Create Contact",
    category="action",
    description="Create a contact in HubSpot CRM.",
    schema=simple_schema(
        {
            "email": {"type": "string", "format": "email"},
            "first_name": {"type": "string"},
            "last_name": {"type": "string"},
        },
        required=["email"],
    ),
    execute=execute,
)
