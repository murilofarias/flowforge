from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Literal


Category = Literal["trigger", "action", "transform", "logic", "ai"]


@dataclass
class NodeContext:
    node_id: str
    config: dict[str, Any]
    inputs: dict[str, Any]  # outputs keyed by source node id
    trigger_payload: dict[str, Any] | None
    fixture_mode: bool


@dataclass
class NodeResult:
    output: dict[str, Any]
    branch: str | None = None  # optional output handle name for branching
    skipped: bool = False
    logs: list[str] = field(default_factory=list)


@dataclass
class NodeDefinition:
    type: str
    name: str
    category: Category
    description: str
    schema: dict[str, Any]  # JSON schema for config
    execute: Callable[[NodeContext], NodeResult]

    def to_catalog(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "schema": self.schema,
        }


def simple_schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
    }
