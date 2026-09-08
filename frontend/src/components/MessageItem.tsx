import React from "react";
import { User, Sparkles, CheckCircle2, AlertTriangle } from "lucide-react";
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
            <div style={{ lineHeight: 1.6 }}>
              {renderContentWithCitations(message.content)}
            </div>

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

            <div className="message-meta">
              {message.provider && (
                <span>Provider: {message.provider} ({message.model})</span>
              )}
              {message.chunks_used !== undefined && (
                <span>• {message.chunks_used} chunks retrieved</span>
              )}
              {message.validation_status === "valid" && (
                <span style={{ display: "flex", alignItems: "center", gap: "3px", color: "var(--accent-emerald)" }}>
                  <CheckCircle2 size={12} /> Citations verified
                </span>
              )}
              {message.validation_status === "cleaned_invalid" && (
                <span style={{ display: "flex", alignItems: "center", gap: "3px", color: "var(--accent-amber)" }}>
                  <AlertTriangle size={12} /> Hallucinated tags filtered
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
