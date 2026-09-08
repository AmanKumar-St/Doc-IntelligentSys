import React from "react";
import { FileText, Cpu, Database, Search, MessageSquare } from "lucide-react";
import type { SystemHealth } from "../types";

interface NavbarProps {
  health: SystemHealth | null;
  activeTab: "chat" | "search";
  setActiveTab: (tab: "chat" | "search") => void;
}

export const Navbar: React.FC<NavbarProps> = ({ health, activeTab, setActiveTab }) => {
  return (
    <header className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <FileText size={22} />
        </div>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span className="brand-title">DocIntelligent</span>
            <span className="brand-badge">RAG v0.1</span>
          </div>
        </div>
      </div>

      {/* Mode Switcher Tabs */}
      <div style={{ display: "flex", gap: "0.5rem", background: "rgba(30, 41, 59, 0.6)", padding: "3px", borderRadius: "8px" }}>
        <button
          onClick={() => setActiveTab("chat")}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            padding: "6px 14px",
            borderRadius: "6px",
            border: "none",
            fontSize: "0.85rem",
            fontWeight: 600,
            cursor: "pointer",
            background: activeTab === "chat" ? "var(--accent-blue)" : "transparent",
            color: activeTab === "chat" ? "#090d16" : "var(--text-secondary)",
            transition: "all 0.2s",
          }}
        >
          <MessageSquare size={16} />
          Chat & QA
        </button>
        <button
          onClick={() => setActiveTab("search")}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            padding: "6px 14px",
            borderRadius: "6px",
            border: "none",
            fontSize: "0.85rem",
            fontWeight: 600,
            cursor: "pointer",
            background: activeTab === "search" ? "var(--accent-blue)" : "transparent",
            color: activeTab === "search" ? "#090d16" : "var(--text-secondary)",
            transition: "all 0.2s",
          }}
        >
          <Search size={16} />
          Vector Search
        </button>
      </div>

      <div className="nav-status">
        <div className="status-indicator">
          <div className="status-dot" />
          <span>{health ? health.status.toUpperCase() : "CONNECTING"}</span>
        </div>

        {health && (
          <div style={{ display: "flex", gap: "0.5rem", fontSize: "0.75rem", color: "var(--text-muted)" }}>
            <span style={{ display: "flex", alignItems: "center", gap: "3px" }}>
              <Cpu size={14} color="var(--accent-blue)" /> {health.generation_provider}
            </span>
            <span style={{ display: "flex", alignItems: "center", gap: "3px" }}>
              <Database size={14} color="var(--accent-emerald)" /> Qdrant ({health.storage_mode})
            </span>
          </div>
        )}
      </div>
    </header>
  );
};
