import pytest
from app.services.workflow import topological_order, execute_graph, GraphError


def test_topological_order_linear():
    nodes = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    edges = [{"source": "a", "target": "b"}, {"source": "b", "target": "c"}]
    assert topological_order(nodes, edges) == ["a", "b", "c"]


def test_topological_order_cycle():
    nodes = [{"id": "a"}, {"id": "b"}]
    edges = [{"source": "a", "target": "b"}, {"source": "b", "target": "a"}]
    with pytest.raises(GraphError):
        topological_order(nodes, edges)


def test_execute_graph_empty():
    status, logs, outputs = execute_graph({"nodes": [], "edges": []})
    assert status == "success"
    assert outputs == {}


def test_execute_graph_branching_filter_skips_downstream():
    graph = {
        "nodes": [
            {"id": "t", "type": "webhook_trigger", "config": {}},
            {"id": "f", "type": "filter", "config": {"condition": "False"}},
            {"id": "a", "type": "slack_send_message", "config": {"text": "hi"}},
        ],
        "edges": [
            {"id": "e1", "source": "t", "target": "f"},
            {"id": "e2", "source": "f", "target": "a"},
        ],
    }
    status, logs, _ = execute_graph(graph, trigger_payload={"x": 1}, fixture_mode=True)
    assert status == "success"
    node_status = {l["node_id"]: l["status"] for l in logs}
    assert node_status["f"] == "skipped"
    assert node_status["a"] == "skipped"


def test_execute_graph_error_propagates():
    graph = {
        "nodes": [{"id": "t", "type": "does_not_exist", "config": {}}],
        "edges": [],
    }
    status, logs, _ = execute_graph(graph, fixture_mode=True)
    assert status == "failed"
    assert logs[0]["status"] == "failed"
