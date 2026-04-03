"""Sample workflows used for seeding and tests."""
from __future__ import annotations

LEAD_ENRICHMENT = {
    "name": "Lead Enrichment -> HubSpot + Slack",
    "description": "Webhook receives a lead, AI enriches it, sync to HubSpot, notify Slack.",
    "graph": {
        "nodes": [
            {
                "id": "trigger",
                "type": "webhook_trigger",
                "label": "Incoming Lead",
                "config": {"path": "lead", "verify_signature": True},
                "position": {"x": 80, "y": 200},
            },
            {
                "id": "enrich",
                "type": "openai_chat",
                "label": "Enrich Summary",
                "config": {"model": "gpt-4o-mini", "prompt": "Summarize this lead for sales"},
                "position": {"x": 340, "y": 140},
            },
            {
                "id": "shape",
                "type": "transform",
                "label": "Shape Contact",
                "config": {
                    "mapping": {
                        "email": "trigger['email']",
                        "first_name": "trigger['first_name']",
                        "last_name": "trigger['last_name']",
                    }
                },
                "position": {"x": 600, "y": 140},
            },
            {
                "id": "hubspot",
                "type": "hubspot_create_contact",
                "label": "Create Contact",
                "config": {"email": "noreply@example.com"},
                "position": {"x": 860, "y": 140},
            },
            {
                "id": "notify",
                "type": "slack_send_message",
                "label": "Notify #sales",
                "config": {"channel": "#sales", "text": "New lead captured"},
                "position": {"x": 1120, "y": 200},
            },
        ],
        "edges": [
            {"id": "e1", "source": "trigger", "target": "enrich"},
            {"id": "e2", "source": "enrich", "target": "shape"},
            {"id": "e3", "source": "shape", "target": "hubspot"},
            {"id": "e4", "source": "hubspot", "target": "notify"},
        ],
    },
    "is_active": True,
}


NIGHTLY_SYNC = {
    "name": "Nightly Deal Stage Sync",
    "description": "Cron trigger pulls API data, updates deals, posts summary to Slack.",
    "graph": {
        "nodes": [
            {
                "id": "cron",
                "type": "schedule_trigger",
                "label": "Nightly 2am",
                "config": {"cron": "0 2 * * *"},
                "position": {"x": 80, "y": 200},
            },
            {
                "id": "fetch",
                "type": "http_request",
                "label": "Fetch Pipeline",
                "config": {"method": "GET", "url": "https://example.com/api/deals"},
                "position": {"x": 340, "y": 200},
            },
            {
                "id": "gate",
                "type": "filter",
                "label": "Only if non-empty",
                "config": {"condition": "inputs['fetch']['status'] == 200"},
                "position": {"x": 600, "y": 200},
            },
            {
                "id": "update",
                "type": "hubspot_update_deal",
                "label": "Advance Stage",
                "config": {"deal_id": "123", "stage": "decision"},
                "position": {"x": 860, "y": 200},
            },
        ],
        "edges": [
            {"id": "e1", "source": "cron", "target": "fetch"},
            {"id": "e2", "source": "fetch", "target": "gate"},
            {"id": "e3", "source": "gate", "target": "update"},
        ],
    },
    "is_active": True,
}


ALL = [LEAD_ENRICHMENT, NIGHTLY_SYNC]
