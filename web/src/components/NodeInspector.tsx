import { useMemo } from "react";
import { useWorkflowStore } from "../store/workflow";
import { CATEGORY_STYLES } from "../lib/nodeCatalog";

export default function NodeInspector() {
  const { selectedNodeId, nodes, catalog, updateNode, removeNode } = useWorkflowStore();
  const node = useMemo(() => nodes.find((n) => n.id === selectedNodeId), [nodes, selectedNodeId]);
  const defn = useMemo(() => catalog.find((c) => c.type === node?.type), [catalog, node]);

  if (!node || !defn) {
    return (
      <aside className="w-80 border-l border-black/5 bg-white/70 backdrop-blur p-6 text-sm text-ink/60">
        Select a node to edit its configuration.
      </aside>
    );
  }

  const schemaProps: Record<string, any> = defn.schema?.properties || {};
  const required: string[] = defn.schema?.required || [];
  const cat = CATEGORY_STYLES[defn.category];

  const setConfig = (key: string, val: any) =>
    updateNode(node.id, { config: { ...node.config, [key]: val } });

  return (
    <aside className="w-80 border-l border-black/5 bg-white/80 backdrop-blur overflow-y-auto">
      <div className="p-4 border-b border-black/5 flex items-center gap-2">
        <span className={`w-2.5 h-2.5 rounded-full ${cat?.dot}`} />
        <div className="flex-1">
          <div className="font-semibold">{defn.name}</div>
          <div className="text-[11px] text-ink/60">{defn.description}</div>
        </div>
        <button
          onClick={() => removeNode(node.id)}
          className="text-xs text-red-500 hover:underline"
        >
          delete
        </button>
      </div>
      <div className="p-4 space-y-4">
        <div>
          <label className="text-xs font-medium text-ink/70">Label</label>
          <input
            className="mt-1 w-full rounded-lg border border-black/10 px-3 py-1.5 text-sm"
            value={node.label || ""}
            onChange={(e) => updateNode(node.id, { label: e.target.value })}
            placeholder={defn.name}
          />
        </div>
        {Object.entries(schemaProps).map(([key, schema]: [string, any]) => {
          const val = node.config?.[key] ?? "";
          const isReq = required.includes(key);
          const type = schema.type || "string";
          if (schema.enum) {
            return (
              <Field key={key} label={key} required={isReq}>
                <select
                  className="w-full rounded-lg border border-black/10 px-3 py-1.5 text-sm bg-white"
                  value={val}
                  onChange={(e) => setConfig(key, e.target.value)}
                >
                  <option value="">—</option>
                  {schema.enum.map((o: string) => (
                    <option key={o} value={o}>{o}</option>
                  ))}
                </select>
              </Field>
            );
          }
          if (type === "number") {
            return (
              <Field key={key} label={key} required={isReq}>
                <input
                  type="number"
                  className="w-full rounded-lg border border-black/10 px-3 py-1.5 text-sm"
                  value={val}
                  onChange={(e) => setConfig(key, parseFloat(e.target.value))}
                />
              </Field>
            );
          }
          if (type === "boolean") {
            return (
              <Field key={key} label={key} required={isReq}>
                <input
                  type="checkbox"
                  checked={!!val}
                  onChange={(e) => setConfig(key, e.target.checked)}
                />
              </Field>
            );
          }
          if (type === "object") {
            return (
              <Field key={key} label={key} required={isReq} hint="JSON">
                <textarea
                  className="w-full rounded-lg border border-black/10 px-3 py-2 text-xs font-mono min-h-[90px]"
                  value={JSON.stringify(val || {}, null, 2)}
                  onChange={(e) => {
                    try {
                      setConfig(key, JSON.parse(e.target.value || "{}"));
                    } catch {
                      /* ignore */
                    }
                  }}
                />
              </Field>
            );
          }
          return (
            <Field key={key} label={key} required={isReq} hint={schema.description}>
              <input
                className="w-full rounded-lg border border-black/10 px-3 py-1.5 text-sm"
                value={val}
                onChange={(e) => setConfig(key, e.target.value)}
                placeholder={schema.default != null ? String(schema.default) : ""}
              />
            </Field>
          );
        })}
      </div>
    </aside>
  );
}

function Field({
  label, required, hint, children,
}: { label: string; required?: boolean; hint?: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="flex items-center gap-1 text-xs font-medium text-ink/70">
        {label}
        {required && <span className="text-red-500">*</span>}
      </label>
      {hint && <div className="text-[11px] text-ink/50 mb-1">{hint}</div>}
      <div className="mt-1">{children}</div>
    </div>
  );
}
