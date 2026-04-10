import { useToastStore } from "../store/workflow";
import clsx from "clsx";

export default function Toast() {
  const messages = useToastStore((s) => s.messages);
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2">
      {messages.map((m) => (
        <div
          key={m.id}
          className={clsx(
            "rounded-xl px-4 py-2 text-sm shadow-pop text-white animate-[slideIn_.2s_ease]",
            m.kind === "success" && "bg-trigger-500",
            m.kind === "error" && "bg-red-500",
            m.kind === "info" && "bg-ink",
          )}
        >
          {m.text}
        </div>
      ))}
    </div>
  );
}
