import { NavLink, Route, Routes, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Editor from "./pages/Editor";
import Runs from "./pages/Runs";
import RunDetail from "./pages/RunDetail";
import Toast from "./components/Toast";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-black/5 bg-white/80 backdrop-blur sticky top-0 z-20">
        <div className="mx-auto max-w-7xl px-6 py-3 flex items-center gap-6">
          <NavLink to="/" className="flex items-center gap-2 font-semibold text-lg">
            <span className="inline-block w-6 h-6 rounded-lg bg-gradient-to-br from-trigger-500 via-action-500 to-ai-500" />
            FlowForge
          </NavLink>
          <nav className="flex gap-1 text-sm">
            {[
              { to: "/", label: "Dashboard", end: true },
              { to: "/runs", label: "Runs" },
            ].map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.end}
                className={({ isActive }) =>
                  "px-3 py-1.5 rounded-lg " +
                  (isActive ? "bg-ink text-white" : "hover:bg-black/5")
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto text-xs text-ink/60">fixture mode</div>
        </div>
      </header>
      <main className="flex-1 flex flex-col">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/editor/:id" element={<Editor />} />
          <Route path="/runs" element={<Runs />} />
          <Route path="/runs/:id" element={<RunDetail />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
      <Toast />
    </div>
  );
}
