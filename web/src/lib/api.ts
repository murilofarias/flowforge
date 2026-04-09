const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function j<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export interface WorkflowNode {
  id: string;
  type: string;
  label?: string | null;
  config: Record<string, any>;
  position: { x: number; y: number };
}
export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  source_handle?: string | null;
  target_handle?: string | null;
}
export interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}
export interface Workflow {
  id: string;
  name: string;
  description: string | null;
  graph: WorkflowGraph;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
export interface Run {
  id: string;
  workflow_id: string;
  status: "pending" | "running" | "success" | "failed";
  trigger_payload: Record<string, any> | null;
  node_logs: any[];
  error: string | null;
  started_at: string;
  finished_at: string | null;
}
export interface NodeDef {
  type: string;
  name: string;
  category: "trigger" | "action" | "transform" | "logic" | "ai";
  description: string;
  schema: any;
}

export const api = {
  listWorkflows: () => j<Workflow[]>("/api/workflows"),
  getWorkflow: (id: string) => j<Workflow>(`/api/workflows/${id}`),
  createWorkflow: (name: string) =>
    j<Workflow>("/api/workflows", {
      method: "POST",
      body: JSON.stringify({ name, graph: { nodes: [], edges: [] } }),
    }),
  updateWorkflow: (id: string, patch: Partial<Workflow>) =>
    j<Workflow>(`/api/workflows/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),
  deleteWorkflow: (id: string) => j<void>(`/api/workflows/${id}`, { method: "DELETE" }),
  runWorkflow: (id: string, payload?: any) =>
    j<Run>(`/api/workflows/${id}/run`, {
      method: "POST",
      body: JSON.stringify({ payload: payload || null }),
    }),
  listRuns: (workflowId?: string) =>
    j<Run[]>(`/api/runs${workflowId ? `?workflow_id=${workflowId}` : ""}`),
  getRun: (id: string) => j<Run>(`/api/runs/${id}`),
  catalog: () => j<{ nodes: NodeDef[] }>(`/api/nodes/catalog`),
};
