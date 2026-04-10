import type { Run } from "../lib/api";
import clsx from "clsx";

const STATUS_STYLE: Record<string, string> = {
  success: "bg-trigger-50 text-trigger-700 border-trigger-500/20",
  failed: "bg-red-50 text-red-700 border-red-500/20",
  skipped: "bg-black/5 text-ink/60 border-black/10",
  running: "bg-action-50 text-action-700 border-action-500/20",
};

export default function RunTimeline({ run }: { run: Run }) {
  return (
    <ol className="relative border-l border-black/10 ml-3 space-y-4">
      {run.node_logs.map((log: any, i: number) => (
        <li key={i} className="ml-4">
          <div className="absolute -left-[7px] w-3 h-3 rounded-full border-2 border-white bg-ink/40" />
          <div
            className={clsx(
              "rounded-xl border px-4 py-3 shadow-card",
              STATUS_STYLE[log.status] || STATUS_STYLE.skipped,
            )}
          >
            <div className="flex items-center justify-between">
              <div className="font-medium text-sm">
                <span className="font-mono text-xs text-ink/60 mr-2">{log.node_id}</span>
                {log.type}
              </div>
              <span className="pill bg-white/60 border border-black/5">{log.status}</span>
            </div>
            {log.logs?.length > 0 && (
              <ul className="mt-2 text-xs text-ink/70 font-mono space-y-0.5">
                {log.logs.map((l: string, j: number) => <li key={j}>&gt; {l}</li>)}
              </ul>
            )}
            {log.output && (
              <details className="mt-2">
                <summary className="text-xs text-ink/50 cursor-pointer">output</summary>
                <pre className="text-[11px] font-mono bg-white/70 rounded-lg p-2 mt-1 overflow-auto">
                  {JSON.stringify(log.output, null, 2)}
                </pre>
              </details>
            )}
            {log.error && (
              <div className="mt-1 text-xs text-red-700 font-mono">error: {log.error}</div>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
