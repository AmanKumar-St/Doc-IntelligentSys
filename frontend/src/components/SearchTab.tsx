import React, { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import type { SearchResult, Citation } from "../types";
import { semanticSearch } from "../api/client";

interface SearchTabProps {
  selectedDocId: string | null;
  onCitationClick: (citation: Citation) => void;
}

export const SearchTab: React.FC<SearchTabProps> = ({ selectedDocId, onCitationClick }) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [topK, setTopK] = useState(6);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    try {
      const data = await semanticSearch(query, topK, selectedDocId || undefined);
      setResults(data);
    } catch (err: any) {
      alert(`Search error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: "1.5rem", flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div>
        <h2 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "0.5rem" }}>Semantic Vector Search</h2>
        <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
          Direct dense vector retrieval testbed. Query Qdrant and inspect retrieved chunks and similarity scores.
        </p>
      </div>

      <form onSubmit={handleSearch} style={{ display: "flex", gap: "0.75rem" }}>
        <input
          type="text"
          placeholder="Enter search query (e.g. 'bearer token authentication' or 'leave days')..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            flex: 1,
            background: "var(--bg-input)",
            border: "1px solid var(--border-color)",
            borderRadius: "10px",
            padding: "0.75rem 1rem",
            color: "var(--text-primary)",
            outline: "none",
          }}
        />
        <select
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          style={{
            background: "var(--bg-input)",
            border: "1px solid var(--border-color)",
            borderRadius: "10px",
            padding: "0.75rem",
            color: "var(--text-primary)",
          }}
        >
          <option value={3}>Top 3</option>
          <option value={6}>Top 6</option>
          <option value={10}>Top 10</option>
          <option value={20}>Top 20</option>
        </select>
        <button
          type="submit"
          className="btn-send"
          disabled={!query.trim() || isLoading}
          style={{ padding: "0 1.25rem" }}
        >
          {isLoading ? <Loader2 className="animate-spin" size={16} /> : <Search size={16} />}
          <span>Search</span>
        </button>
      </form>

      {results.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 600 }}>
            {results.length} Chunks Retrieved & Scored:
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(400px, 1fr))", gap: "1rem" }}>
            {results.map((r) => (
              <div
                key={r.chunk_id}
                className="doc-card"
                style={{
                  flexDirection: "column",
                  alignItems: "stretch",
                  padding: "1rem",
                  gap: "0.75rem",
                  cursor: "pointer",
                }}
                onClick={() =>
                  onCitationClick({
                    id: r.citation_id,
                    chunk_id: r.chunk_id,
                    document_id: r.document_id,
                    source: r.source,
                    section: r.section,
                    page: r.page,
                    heading_path: r.heading_path,
                    snippet: r.text,
                    score: r.score,
                  })
                }
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span className="citation-pill">[{r.citation_id}]</span>
                  <span style={{ fontSize: "0.75rem", color: "var(--accent-emerald)", fontWeight: 600 }}>
                    Score: {(r.score * 100).toFixed(1)}%
                  </span>
                </div>

                <div style={{ fontSize: "0.82rem", color: "var(--text-primary)", fontWeight: 600 }}>
                  {r.source} {r.heading_path?.length ? `• ${r.heading_path.join(" > ")}` : ""}
                </div>

                <div style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.5, maxHeight: "120px", overflow: "hidden" }}>
                  {r.text}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
