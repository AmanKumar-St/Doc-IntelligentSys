import React from "react";
import { X, Check, Copy, Hash } from "lucide-react";
import type { Citation } from "../types";

interface CitationInspectorProps {
  citation: Citation | null;
  onClose: () => void;
}

export const CitationInspector: React.FC<CitationInspectorProps> = ({ citation, onClose }) => {
  const [copied, setCopied] = React.useState(false);

  if (!citation) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(citation.snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="citation-drawer-overlay" onClick={onClose}>
      <div className="citation-drawer" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div className="drawer-title">
            <span className="citation-pill" style={{ fontSize: "0.9rem", padding: "3px 10px" }}>
              [{citation.id}]
            </span>
            <span>Citation Inspector</span>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="drawer-content">
          <div className="citation-meta-box">
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
              <span style={{ color: "var(--text-muted)" }}>Source Document:</span>
              <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{citation.source}</span>
            </div>

            {citation.heading_path && citation.heading_path.length > 0 && (
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                <span style={{ color: "var(--text-muted)" }}>Section Hierarchy:</span>
                <span style={{ color: "var(--accent-blue)", textAlign: "right", maxWidth: "60%" }}>
                  {citation.heading_path.join(" > ")}
                </span>
              </div>
            )}

            {citation.page && (
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                <span style={{ color: "var(--text-muted)" }}>Page Number:</span>
                <span>Page {citation.page}</span>
              </div>
            )}

            {citation.score !== undefined && citation.score !== null && (
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-muted)" }}>Retrieval Score:</span>
                <span style={{ color: "var(--accent-emerald)", fontWeight: 600 }}>
                  {(citation.score * 100).toFixed(1)}% match
                </span>
              </div>
            )}
          </div>

          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
              <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)" }}>
                EXACT GROUNDED PASSAGE
              </span>
              <button
                onClick={handleCopy}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  background: "transparent",
                  border: "none",
                  color: "var(--accent-blue)",
                  fontSize: "0.75rem",
                  cursor: "pointer",
                }}
              >
                {copied ? <Check size={14} color="var(--accent-emerald)" /> : <Copy size={14} />}
                {copied ? "Copied" : "Copy Snippet"}
              </button>
            </div>
            <div className="citation-passage-box">
              {citation.snippet}
            </div>
          </div>

          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "auto", padding: "0.75rem", background: "rgba(30, 41, 59, 0.3)", borderRadius: "8px" }}>
            <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
              <Hash size={12} /> Chunk ID: <code>{citation.chunk_id}</code>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
