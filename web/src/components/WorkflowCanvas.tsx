import { useCallback, useMemo } from "react";
import ReactFlow, {
  Background, Controls, MiniMap, addEdge, applyEdgeChanges, applyNodeChanges,
  Connection, Edge, EdgeChange, Node, NodeChange, Handle, Position,
} from "reactflow";
import { useWorkflowStore } from "../store/workflow";
import { CATEGORY_STYLES } from "../lib/nodeCatalog";

function FlowNode({ data, selected }: { data: any; selected?: boolean }) {
  const cat = CATEGORY_STYLES[data.category] || CATEGORY_STYLES.action;
  return (
    <div
      className={`node-card ${cat.bg} ${selected ? "ring-2 ring-ink/30" : ""}`}
    >
      <Handle type="target" position={Position.Left} className="!bg-ink/40" />
      <div className="flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full ${cat.dot}`} />
        <div className="flex-1">
          <div className="text-xs uppercase tracking-wide text-ink/50">{cat.label}</div>
          <div className="font-semibold text-sm">{data.label || data.typeName}</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-ink/40" />
    </div>
  );
}

const nodeTypes = { flow: FlowNode };

export default function WorkflowCanvas() {
  const { nodes, edges, setNodes, setEdges, select, catalog, addNode } = useWorkflowStore();

  const rfNodes = useMemo<Node[]>(
    () =>
      nodes.map((n) => {
        const defn = catalog.find((c) => c.type === n.type);
        return {
          id: n.id,
          type: "flow",
          position: n.position,
          data: {
            label: n.label,
            typeName: defn?.name || n.type,
            category: defn?.category || "action",
          },
        };
      }),
    [nodes, catalog],
  );
  const rfEdges = useMemo<Edge[]>(
    () =>
      edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        animated: true,
        style: { stroke: "#2a2a33", strokeWidth: 1.6 },
      })),
    [edges],
  );

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      const next = applyNodeChanges(changes, rfNodes);
      setNodes(
        next.map((n) => {
          const orig = nodes.find((x) => x.id === n.id)!;
          return { ...orig, position: { x: n.position.x, y: n.position.y } };
        }),
      );
    },
    [rfNodes, nodes, setNodes],
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      const next = applyEdgeChanges(changes, rfEdges);
      setEdges(next.map((e) => ({ id: e.id, source: e.source, target: e.target })));
    },
    [rfEdges, setEdges],
  );

  const onConnect = useCallback(
    (c: Connection) => {
      const next = addEdge({ ...c, id: `e_${c.source}_${c.target}_${Date.now()}` }, rfEdges);
      setEdges(next.map((e) => ({ id: e.id, source: e.source!, target: e.target! })));
    },
    [rfEdges, setEdges],
  );

  const onDrop = (event: React.DragEvent) => {
    event.preventDefault();
    const type = event.dataTransfer.getData("application/flowforge-node");
    if (!type) return;
    const bounds = (event.target as HTMLElement).closest(".react-flow")?.getBoundingClientRect();
    const position = {
      x: event.clientX - (bounds?.left || 0) - 100,
      y: event.clientY - (bounds?.top || 0) - 30,
    };
    const id = `n_${Math.random().toString(36).slice(2, 8)}`;
    addNode({ id, type, label: null, config: {}, position });
  };

  return (
    <div
      className="flex-1 grid-bg"
      onDragOver={(e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
      }}
      onDrop={onDrop}
    >
      <ReactFlow
        nodes={rfNodes}
        edges={rfEdges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={(_, n) => select(n.id)}
        onPaneClick={() => select(null)}
        fitView
      >
        <Background gap={22} size={1} color="rgba(40,38,60,0.08)" />
        <MiniMap
          pannable
          zoomable
          maskColor="rgba(253,250,244,0.7)"
          nodeColor={(n) => {
            const c = (n.data as any)?.category || "action";
            return (
              { trigger: "#34a86b", action: "#3b7bdb", transform: "#8a63d2", logic: "#d9a13a", ai: "#d85590" } as any
            )[c];
          }}
        />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
