import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, type Run } from "../lib/api";
import { StatusPill } from "./Dashboard";
import RunTimeline from "../components/RunTimeline";

export default function RunDetail() {
  const { id } = useParams();
  const [run, setRun] = useState<Run | null>(null);

  useEffect(() => {
    if (!id) return;
    let alive = true;
    const tick = async () => {
      try {
        const r = await api.getRun(id);
        if (!alive) return;
        setRun(r);
        if (r.status === "success" || r.status === "failed") return;
        setTimeout(tick, 1000);
      } catch {
        /* ignore */
      }
    };
    tick();
    return () => {
      alive = false;
    };
  }, [id]);

  if (!run) return <div className="p-10 text-ink/60">Loading run...</div>;

  return (
    <div className="mx-auto max-w-5xl px-6 py-8 w-full">
      <div className="flex items-center gap-3 mb-6">
        <Link to="/runs" className="text-sm text-ink/60 hover:underline">← Runs</Link>
        <h1 className="text-xl font-semibold">Run {run.id.slice(0, 8)}</h1>
        <StatusPill status={run.status} />
        <span className="ml-auto text-xs text-ink/60">
          {new Date(run.started_at).toLocaleString()}
          {run.finished_at && ` → ${new Date(run.finished_at).toLocaleString()}`}
        </span>
      </div>

      {run.error && (
        <div className="mb-6 rounded-xl border border-red-500/20 bg-red-50 text-red-700 px-4 py-3 text-sm font-mono">
          {run.error}
        </div>
      )}

      <h2 className="text-sm font-semibold text-ink/70 mb-3">Timeline</h2>
      <RunTimeline run={run} />
    </div>
  );
}
