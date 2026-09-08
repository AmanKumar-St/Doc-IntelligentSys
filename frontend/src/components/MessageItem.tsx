import { User, Sparkles, CheckCircle2, AlertTriangle, FileCode, ShieldCheck } from "lucide-react";
import type { ChatMessage, Citation } from "../types";

interface MessageItemProps {
  message: ChatMessage;
  onCitationClick: (citation: Citation) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message, onCitationClick }) => {
  const isUser = message.role === "user";

  const renderContentWithCitations = (text: string) => {
    const parts = text.split(/(\[C\d+\])/g);

    return parts.map((part, index) => {
      const match = part.match(/^\[(C\d+)\]$/);
      if (match) {
        const citationId = match[1];
        const citationObj = message.citations?.find((c) => c.id === citationId);

        return (
          <button
            key={index}
            className="citation-pill"
            title={citationObj ? `Click to inspect source: ${citationObj.source}` : "View Citation"}
            onClick={() => {
              if (citationObj) {
                onCitationClick(citationObj);
              }
            }}
          >
            [{citationId}]
          </button>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className={`message-row ${message.role}`}>
      <div className={`message-avatar ${message.role}`}>
        {isUser ? <User size={18} /> : <Sparkles size={18} />}
      </div>

      <div className="message-content">
        {isUser ? (
          <div>{message.content}</div>
        ) : (
          <div>
            {/* Task Badge header */}
            {message.task_type && (
              <div style={{ display: "inline-flex", alignItems: "center", gap: "4px", fontSize: "0.68rem", fontWeight: 700, padding: "2px 6px", background: "rgba(99, 102, 241, 0.2)", color: "var(--accent-indigo)", borderRadius: "4px", textTransform: "uppercase", marginBottom: "0.5rem" }}>
                Mode: {message.task_type}
              </div>
            )}

            {/* Main Response Text */}
            <div style={{ lineHeight: 1.6 }}>
              {renderContentWithCitations(message.content)}
            </div>

            {/* Structured JSON Output Box if present */}
            {message.structured_data && (
              <div style={{ marginTop: "0.85rem", background: "#090d16", border: "1px solid var(--border-color)", borderRadius: "8px", padding: "0.85rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.75rem", fontWeight: 600, color: "var(--accent-blue)", marginBottom: "0.5rem" }}>
                  <FileCode size={14} /> STRUCTURED JSON OUTPUT
                </div>
                <pre style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "0.8rem", color: "#a7f3d0", overflowX: "auto", margin: 0 }}>
                  {JSON.stringify(message.structured_data, null, 2)}
                </pre>
              </div>
            )}

            {/* Citations Footer */}
            {message.citations && message.citations.length > 0 && (
              <div className="citations-footer">
                <span style={{ fontSize: "0.72rem", color: "var(--text-muted)", alignSelf: "center", marginRight: "4px" }}>
                  Sources cited:
                </span>
                {message.citations.map((c) => (
                  <button
                    key={c.id}
                    className="citation-pill"
                    onClick={() => onCitationClick(c)}
                  >
                    [{c.id}] {c.source}
                  </button>
                ))}
              </div>
            )}

            {/* Validation Metadata Status Bar */}
            <div className="message-meta">
              {message.provider && (
                <span>Provider: {message.provider} ({message.model})</span>
              )}
              {message.chunks_used !== undefined && (
                <span>• {message.chunks_used} chunks retrieved</span>
              )}

              {message.validation && (
                <div style={{ display: "flex", gap: "8px", alignItems: "center", marginLeft: "auto" }}>
                  {message.validation.structure_valid && (
                    <span style={{ display: "flex", alignItems: "center", gap: "2px", color: "var(--accent-emerald)" }} title="Structure Validated">
                      <ShieldCheck size={12} /> Format Valid
                    </span>
                  )}
                  {message.validation.factuality_status === "supported" && (
                    <span style={{ display: "flex", alignItems: "center", gap: "2px", color: "var(--accent-emerald)" }} title="Numerical and Factually Grounded">
                      <CheckCircle2 size={12} /> Factually Grounded ({Math.round(message.validation.factuality_score * 100)}%)
                    </span>
                  )}
                  {message.validation.factuality_status === "partially_supported" && (
                    <span style={{ display: "flex", alignItems: "center", gap: "2px", color: "var(--accent-amber)" }} title="Partial Grounding Warning">
                      <AlertTriangle size={12} /> Partial Grounding ({Math.round(message.validation.factuality_score * 100)}%)
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
