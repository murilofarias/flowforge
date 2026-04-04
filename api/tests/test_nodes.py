from app.services.nodes import get_node, catalog
from app.services.nodes.base import NodeContext


def _ctx(config=None, inputs=None, trigger=None):
    return NodeContext(
        node_id="n1",
        config=config or {},
        inputs=inputs or {},
        trigger_payload=trigger,
        fixture_mode=True,
    )


def test_catalog_has_all_types():
    types = {n["type"] for n in catalog()}
    for expected in [
        "http_request",
        "hubspot_create_contact",
        "hubspot_update_deal",
        "salesforce_create_lead",
        "slack_send_message",
        "openai_chat",
        "transform",
        "filter",
        "delay",
        "webhook_trigger",
        "schedule_trigger",
    ]:
        assert expected in types


def test_http_fixture():
    defn = get_node("http_request")
    res = defn.execute(_ctx({"method": "GET", "url": "https://api.example.com"}))
    assert res.output["status"] == 200
    assert res.output["body"]["fixture"] is True


def test_transform_mapping():
    defn = get_node("transform")
    res = defn.execute(_ctx(
        {"mapping": {"double": "inputs['src']['n'] * 2", "who": "trigger['name']"}},
        inputs={"src": {"n": 5}},
        trigger={"name": "ada"},
    ))
    assert res.output == {"double": 10, "who": "ada"}


def test_filter_true_passes():
    defn = get_node("filter")
    res = defn.execute(_ctx({"condition": "1 < 2"}))
    assert res.skipped is False
    assert res.branch == "true"


def test_filter_false_skips():
    defn = get_node("filter")
    res = defn.execute(_ctx({"condition": "1 > 2"}))
    assert res.skipped is True
    assert res.branch == "false"


def test_openai_fixture():
    defn = get_node("openai_chat")
    res = defn.execute(_ctx({"prompt": "hello"}))
    assert "fixture" in res.output["content"]


def test_slack_fixture():
    defn = get_node("slack_send_message")
    res = defn.execute(_ctx({"channel": "#x", "text": "hi"}))
    assert res.output["sent"] is True
