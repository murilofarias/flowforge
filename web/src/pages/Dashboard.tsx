import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, type Workflow, type Run } from "../lib/api";
import { useToastStore } from "../store/workflow";

export default function Dashboard() {
  const [wfs, setWfs] = useState<Workflow[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);
  const push = useToastStore((s) => s.push);
  const nav = useNavigate();

  useEffect(() => {
    Promise.all([api.listWorkflows().catch(() => []), api.listRuns().catch(() => [])])
      .then(([w, r]) => {
        setWfs(w);
        setRuns(r);
      })
      .finally(() => setLoading(false));
  }, []);

  const onCreate = async () => {
    try {
      const wf = await api.createWorkflow("Untitled workflow");
      push("Workflow created", "success");
      nav(`/editor/${wf.id}`);
    } catch (e: any) {
      push(e.message || "Failed to create", "error");
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-6 py-8 w-full">
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold">Workflows</h1>
          <p className="text-sm text-ink/60">Build visual automations that run on every trigger.</p>
        </div>
        <button
          onClick={onCreate}
          className="rounded-xl bg-ink text-white px-4 py-2 text-sm shadow-card hover:shadow-pop"
        >
          + New workflow
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 mb-10">
        {loading && <div className="text-ink/60">Loading...</div>}
        {!loading && wfs.length === 0 && (
          <div className="col-span-full rounded-2xl bg-white/70 border border-black/5 p-10 text-center">
            <p className="text-ink/60 mb-4">No workflows yet. Start with a blank canvas.</p>
            <button
              onClick={onCreate}
              className="rounded-xl bg-ink text-white px-4 py-2 text-sm"
            >
              + Create your first workflow
            </button>
          </div>
        )}
        {wfs.map((wf) => (
          <Link
            key={wf.id}
            to={`/editor/${wf.id}`}
            className="group rounded-2xl bg-white border border-black/5 p-5 shadow-card hover:shadow-pop transition"
          >
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-lg">{wf.name}</h3>
              <span className={`pill ${wf.is_active ? "bg-trigger-50 text-trigger-700" : "bg-black/5"}`}>
                {wf.is_active ? "active" : "paused"}
              </span>
            </div>
            <p className="text-sm text-ink/60 mt-1 line-clamp-2">{wf.description || "—"}</p>
            <div className="mt-4 flex gap-2 text-xs text-ink/60">
              <span className="pill bg-black/5">{wf.graph.nodes.length} nodes</span>
              <span className="pill bg-black/5">{wf.graph.edges.length} edges</span>
            </div>
          </Link>
        ))}
      </div>

      <h2 className="text-lg font-semibold mb-3">Recent runs</h2>
      <div className="rounded-2xl bg-white border border-black/5 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-black/5 text-ink/60 text-xs uppercase tracking-wide">
            <tr><th className="text-left px-4 py-2">Run</th><th className="text-left px-4 py-2">Workflow</th><th className="text-left px-4 py-2">Status</th><th className="text-left px-4 py-2">Started</th></tr>
          </thead>
          <tbody>
            {runs.slice(0, 8).map((r) => {
              const wf = wfs.find((w) => w.id === r.workflow_id);
              return (
                <tr key={r.id} className="border-t border-black/5 hover:bg-black/[.02]">
                  <td className="px-4 py-2">
                    <Link to={`/runs/${r.id}`} className="font-mono text-xs hover:underline">
                      {r.id.slice(0, 8)}
                    </Link>
                  </td>
                  <td className="px-4 py-2">{wf?.name || r.workflow_id.slice(0, 8)}</td>
                  <td className="px-4 py-2"><StatusPill status={r.status} /></td>
                  <td className="px-4 py-2 text-ink/60">{new Date(r.started_at).toLocaleString()}</td>
                </tr>
              );
            })}
            {runs.length === 0 && (
              <tr><td colSpan={4} className="px-4 py-6 text-center text-ink/50">No runs yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function StatusPill({ status }: { status: string }) {
  const map: Record<string, string> = {
    success: "bg-trigger-50 text-trigger-700",
    failed: "bg-red-50 text-red-700",
    running: "bg-action-50 text-action-700",
    pending: "bg-logic-50 text-logic-700",
  };
  return <span className={`pill ${map[status] || "bg-black/5"}`}>{status}</span>;
}
