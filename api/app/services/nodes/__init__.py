from __future__ import annotations
from typing import Any, Callable

from app.services.nodes.base import NodeContext, NodeResult, NodeDefinition
from app.services.nodes import (
    http_request,
    hubspot_create_contact,
    hubspot_update_deal,
    salesforce_create_lead,
    slack_send_message,
    openai_chat,
    transform,
    filter_node,
    delay,
    webhook_trigger,
    schedule_trigger,
)

REGISTRY: dict[str, NodeDefinition] = {}


def register(defn: NodeDefinition) -> None:
    REGISTRY[defn.type] = defn


for module in (
    webhook_trigger,
    schedule_trigger,
    http_request,
    hubspot_create_contact,
    hubspot_update_deal,
    salesforce_create_lead,
    slack_send_message,
    openai_chat,
    transform,
    filter_node,
    delay,
):
    register(module.definition)


def get_node(type_: str) -> NodeDefinition:
    if type_ not in REGISTRY:
        raise KeyError(f"Unknown node type: {type_}")
    return REGISTRY[type_]


def catalog() -> list[dict[str, Any]]:
    return [defn.to_catalog() for defn in REGISTRY.values()]
