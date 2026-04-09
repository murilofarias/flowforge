import { create } from "zustand";
import type { Workflow, WorkflowNode, WorkflowEdge, NodeDef } from "../lib/api";

interface WorkflowState {
  workflow: Workflow | null;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  selectedNodeId: string | null;
  catalog: NodeDef[];
  setWorkflow: (wf: Workflow) => void;
  setCatalog: (defs: NodeDef[]) => void;
  addNode: (n: WorkflowNode) => void;
  updateNode: (id: string, patch: Partial<WorkflowNode>) => void;
  removeNode: (id: string) => void;
  setNodes: (ns: WorkflowNode[]) => void;
  setEdges: (es: WorkflowEdge[]) => void;
  select: (id: string | null) => void;
}

export const useWorkflowStore = create<WorkflowState>((set) => ({
  workflow: null,
  nodes: [],
  edges: [],
  selectedNodeId: null,
  catalog: [],
  setWorkflow: (wf) => set({ workflow: wf, nodes: wf.graph.nodes, edges: wf.graph.edges }),
  setCatalog: (defs) => set({ catalog: defs }),
  addNode: (n) => set((s) => ({ nodes: [...s.nodes, n] })),
  updateNode: (id, patch) =>
    set((s) => ({ nodes: s.nodes.map((n) => (n.id === id ? { ...n, ...patch } : n)) })),
  removeNode: (id) =>
    set((s) => ({
      nodes: s.nodes.filter((n) => n.id !== id),
      edges: s.edges.filter((e) => e.source !== id && e.target !== id),
      selectedNodeId: s.selectedNodeId === id ? null : s.selectedNodeId,
    })),
  setNodes: (ns) => set({ nodes: ns }),
  setEdges: (es) => set({ edges: es }),
  select: (id) => set({ selectedNodeId: id }),
}));

interface ToastState {
  messages: { id: number; text: string; kind: "info" | "success" | "error" }[];
  push: (text: string, kind?: "info" | "success" | "error") => void;
  remove: (id: number) => void;
}
let toastCounter = 0;
export const useToastStore = create<ToastState>((set) => ({
  messages: [],
  push: (text, kind = "info") => {
    const id = ++toastCounter;
    set((s) => ({ messages: [...s.messages, { id, text, kind }] }));
    setTimeout(() => {
      set((s) => ({ messages: s.messages.filter((m) => m.id !== id) }));
    }, 3500);
  },
  remove: (id) => set((s) => ({ messages: s.messages.filter((m) => m.id !== id) })),
}));
