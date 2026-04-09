import type { NodeDef } from "./api";

export const CATEGORY_STYLES: Record<string, { bg: string; dot: string; label: string }> = {
  trigger:   { bg: "node-cat-trigger",   dot: "bg-trigger-500",   label: "Trigger" },
  action:    { bg: "node-cat-action",    dot: "bg-action-500",    label: "Action" },
  transform: { bg: "node-cat-transform", dot: "bg-transform-500", label: "Transform" },
  logic:     { bg: "node-cat-logic",     dot: "bg-logic-500",     label: "Logic" },
  ai:        { bg: "node-cat-ai",        dot: "bg-ai-500",        label: "AI" },
};

export function groupByCategory(defs: NodeDef[]): Record<string, NodeDef[]> {
  const groups: Record<string, NodeDef[]> = {};
  for (const d of defs) {
    (groups[d.category] ||= []).push(d);
  }
  return groups;
}

// Local fallback if backend is unreachable — keeps the UI functional in isolation.
export const FALLBACK_CATALOG: NodeDef[] = [
  { type: "webhook_trigger", name: "Webhook Trigger", category: "trigger", description: "HTTP trigger", schema: { type: "object", properties: { path: { type: "string" } } } },
  { type: "schedule_trigger", name: "Schedule", category: "trigger", description: "Cron trigger", schema: { type: "object", properties: { cron: { type: "string" } } } },
  { type: "http_request", name: "HTTP Request", category: "action", description: "Make HTTP request", schema: { type: "object", properties: { url: { type: "string" }, method: { type: "string" } } } },
  { type: "hubspot_create_contact", name: "HubSpot Contact", category: "action", description: "Create contact", schema: { type: "object", properties: { email: { type: "string" } } } },
  { type: "slack_send_message", name: "Slack Message", category: "action", description: "Post to Slack", schema: { type: "object", properties: { channel: { type: "string" }, text: { type: "string" } } } },
  { type: "openai_chat", name: "OpenAI Chat", category: "ai", description: "LLM prompt", schema: { type: "object", properties: { prompt: { type: "string" }, model: { type: "string" } } } },
  { type: "transform", name: "Transform", category: "transform", description: "Map fields", schema: { type: "object", properties: { mapping: { type: "object" } } } },
  { type: "filter", name: "Filter", category: "logic", description: "Conditional gate", schema: { type: "object", properties: { condition: { type: "string" } } } },
  { type: "delay", name: "Delay", category: "logic", description: "Wait N seconds", schema: { type: "object", properties: { seconds: { type: "number" } } } },
];
