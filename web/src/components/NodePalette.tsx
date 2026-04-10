import { useWorkflowStore } from "../store/workflow";
import { CATEGORY_STYLES, groupByCategory } from "../lib/nodeCatalog";

export default function NodePalette() {
  const catalog = useWorkflowStore((s) => s.catalog);
  const groups = groupByCategory(catalog);
  const order = ["trigger", "action", "logic", "transform", "ai"];

  const onDragStart = (e: React.DragEvent, type: string) => {
    e.dataTransfer.setData("application/flowforge-node", type);
    e.dataTransfer.effectAllowed = "move";
  };

  return (
    <aside className="w-64 border-r border-black/5 bg-white/60 backdrop-blur overflow-y-auto">
      <div className="p-4 border-b border-black/5">
        <h2 className="text-sm font-semibold">Node palette</h2>
        <p className="text-xs text-ink/60">Drag nodes onto the canvas.</p>
      </div>
      <div className="p-3 space-y-5">
        {order
          .filter((cat) => groups[cat]?.length)
          .map((cat) => (
            <div key={cat}>
              <div className="flex items-center gap-2 px-1 mb-2">
                <span className={`w-2 h-2 rounded-full ${CATEGORY_STYLES[cat]?.dot}`} />
                <span className="text-xs uppercase tracking-wide text-ink/60 font-medium">
                  {CATEGORY_STYLES[cat]?.label}
                </span>
              </div>
              <div className="space-y-1.5">
                {groups[cat].map((n) => (
                  <div
                    key={n.type}
                    draggable
                    onDragStart={(e) => onDragStart(e, n.type)}
                    className={`cursor-grab active:cursor-grabbing rounded-xl border px-3 py-2 text-sm shadow-card ${CATEGORY_STYLES[cat]?.bg}`}
                    title={n.description}
                  >
                    <div className="font-medium">{n.name}</div>
                    <div className="text-[11px] text-ink/60 line-clamp-1">{n.description}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
      </div>
    </aside>
  );
}
