import React from "react";
import { Trash2, Layers } from "lucide-react";
import type { DocumentItem } from "../types";
import { deleteDocument } from "../api/client";

interface DocumentListProps {
  documents: DocumentItem[];
  selectedDocId: string | null;
  onSelectDoc: (id: string | null) => void;
  onRefresh: () => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  selectedDocId,
  onSelectDoc,
  onRefresh,
}) => {
  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this document and its vector embeddings?")) return;
    try {
      await deleteDocument(id);
      if (selectedDocId === id) onSelectDoc(null);
      onRefresh();
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const getBadgeClass = (filename: string) => {
    const ext = filename.split(".").pop()?.toLowerCase() || "";
    if (ext === "pdf") return "doc-badge pdf";
    if (ext === "docx" || ext === "doc") return "doc-badge docx";
    return "doc-badge md";
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", flex: 1, minHeight: 0 }}>
      <div className="section-header">
        <span className="section-title">Indexed Documents ({documents.length})</span>
        {selectedDocId && (
          <button
            onClick={() => onSelectDoc(null)}
            style={{
              background: "transparent",
              border: "none",
              color: "var(--accent-blue)",
              fontSize: "0.75rem",
              cursor: "pointer",
            }}
          >
            Clear Filter
          </button>
        )}
      </div>

      {documents.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem 1rem", color: "var(--text-muted)", fontSize: "0.85rem" }}>
          No documents indexed yet. Upload a file above to begin.
        </div>
      ) : (
        <div className="doc-list">
          {documents.map((doc) => {
            const isSelected = selectedDocId === doc.id;
            const ext = doc.filename.split(".").pop() || "doc";
            return (
              <div
                key={doc.id}
                className="doc-card"
                style={{
                  borderColor: isSelected ? "var(--accent-blue)" : "var(--border-color)",
                  background: isSelected ? "rgba(56, 189, 248, 0.1)" : "var(--bg-card)",
                  cursor: "pointer",
                }}
                onClick={() => onSelectDoc(isSelected ? null : doc.id)}
              >
                <div className="doc-info">
                  <span className={getBadgeClass(doc.filename)}>{ext}</span>
                  <div style={{ display: "flex", flexDirection: "column" }}>
                    <span className="doc-name" title={doc.filename}>
                      {doc.filename}
                    </span>
                    <span className="doc-meta" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <span><Layers size={10} style={{ display: "inline" }} /> {doc.chunk_count} chunks</span>
                      <span>•</span>
                      <span>{(doc.size_bytes / 1024).toFixed(1)} KB</span>
                    </span>
                  </div>
                </div>

                <button
                  className="btn-icon"
                  title="Delete Document"
                  onClick={(e) => handleDelete(e, doc.id)}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
