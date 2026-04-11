import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Run, type Workflow } from "../lib/api";
import { StatusPill } from "./Dashboard";

export default function Runs() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [wfs, setWfs] = useState<Workflow[]>([]);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    api.listRuns().then(setRuns).catch(() => setRuns([]));
    api.listWorkflows().then(setWfs).catch(() => setWfs([]));
  }, []);

  const filtered = runs.filter((r) => (filter === "all" ? true : r.status === filter));

  return (
    <div className="mx-auto max-w-7xl px-6 py-8 w-full">
      <div className="flex items-end justify-between mb-6">
        <h1 className="text-2xl font-semibold">Runs</h1>
        <div className="flex gap-1 text-sm">
          {["all", "pending", "running", "success", "failed"].map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-3 py-1 rounded-lg ${
                filter === s ? "bg-ink text-white" : "bg-white border border-black/10"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>
      <div className="rounded-2xl bg-white border border-black/5 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-black/5 text-ink/60 text-xs uppercase tracking-wide">
            <tr>
              <th className="text-left px-4 py-2">Run</th>
              <th className="text-left px-4 py-2">Workflow</th>
              <th className="text-left px-4 py-2">Status</th>
              <th className="text-left px-4 py-2">Started</th>
              <th className="text-left px-4 py-2">Finished</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => {
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
                  <td className="px-4 py-2 text-ink/60">
                    {r.finished_at ? new Date(r.finished_at).toLocaleString() : "—"}
                  </td>
                </tr>
              );
            })}
            {filtered.length === 0 && (
              <tr><td colSpan={5} className="px-4 py-10 text-center text-ink/50">No runs match.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
