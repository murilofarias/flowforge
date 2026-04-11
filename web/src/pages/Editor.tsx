import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../lib/api";
import { useWorkflowStore, useToastStore } from "../store/workflow";
import { FALLBACK_CATALOG } from "../lib/nodeCatalog";
import NodePalette from "../components/NodePalette";
import NodeInspector from "../components/NodeInspector";
import WorkflowCanvas from "../components/WorkflowCanvas";

export default function Editor() {
  const { id } = useParams();
  const { workflow, nodes, edges, setWorkflow, setCatalog } = useWorkflowStore();
  const push = useToastStore((s) => s.push);
  const [saving, setSaving] = useState(false);
  const [running, setRunning] = useState(false);
  const [lastRunId, setLastRunId] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    api
      .catalog()
      .then((c) => setCatalog(c.nodes))
      .catch(() => setCatalog(FALLBACK_CATALOG));
    api
      .getWorkflow(id)
      .then(setWorkflow)
      .catch((e) => push(e.message || "Workflow not found", "error"));
  }, [id]);

  const onSave = async () => {
    if (!workflow) return;
    setSaving(true);
    try {
      const saved = await api.updateWorkflow(workflow.id, {
        name: workflow.name,
        graph: { nodes, edges },
      });
      setWorkflow(saved);
      push("Workflow saved", "success");
    } catch (e: any) {
      push(e.message || "Save failed", "error");
    } finally {
      setSaving(false);
    }
  };

  const onRun = async () => {
    if (!workflow) return;
    setRunning(true);
    setRunStatus("pending");
    try {
      await onSave();
      const run = await api.runWorkflow(workflow.id, { demo: true });
      setLastRunId(run.id);
      setRunStatus(run.status);
      push(`Run enqueued (${run.id.slice(0, 8)})`, "success");
      const poll = setInterval(async () => {
        try {
          const r = await api.getRun(run.id);
          setRunStatus(r.status);
          if (r.status === "success" || r.status === "failed") {
            clearInterval(poll);
            setRunning(false);
            push(`Run ${r.status}`, r.status === "success" ? "success" : "error");
          }
        } catch {
          clearInterval(poll);
          setRunning(false);
        }
      }, 1000);
    } catch (e: any) {
      push(e.message || "Run failed", "error");
      setRunning(false);
    }
  };

  if (!workflow) {
    return <div className="p-10 text-ink/60">Loading workflow...</div>;
  }

  return (
    <div className="flex-1 flex flex-col">
      <div className="flex items-center gap-3 px-6 py-3 border-b border-black/5 bg-white/70 backdrop-blur">
        <input
          className="font-semibold text-base bg-transparent outline-none border-b border-transparent focus:border-black/10"
          value={workflow.name}
          onChange={(e) => setWorkflow({ ...workflow, name: e.target.value })}
        />
        <span className="text-xs text-ink/50">
          {nodes.length} nodes · {edges.length} edges
        </span>
        {runStatus && (
          <span className="ml-3 pill bg-black/5">
            run: {runStatus}
            {lastRunId && (
              <Link to={`/runs/${lastRunId}`} className="ml-2 underline">view</Link>
            )}
          </span>
        )}
        <div className="ml-auto flex gap-2">
          <button
            onClick={onSave}
            disabled={saving}
            className="rounded-lg border border-black/10 px-3 py-1.5 text-sm hover:bg-black/5"
          >
            {saving ? "Saving..." : "Save"}
          </button>
          <button
            onClick={onRun}
            disabled={running}
            className="rounded-lg bg-trigger-500 text-white px-4 py-1.5 text-sm shadow-card hover:shadow-pop disabled:opacity-50"
          >
            {running ? "Running..." : "▶ Run"}
          </button>
        </div>
      </div>
      <div className="flex-1 flex">
        <NodePalette />
        <WorkflowCanvas />
        <NodeInspector />
      </div>
    </div>
  );
}
