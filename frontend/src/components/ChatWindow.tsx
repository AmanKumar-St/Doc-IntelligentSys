import React, { useState, useRef, useEffect } from "react";
import { Send, Sparkles, AlertCircle, RefreshCw } from "lucide-react";
import type { ChatMessage, Citation } from "../types";
import { MessageItem } from "./MessageItem";
import { sendChatMessage } from "../api/client";

interface ChatWindowProps {
  selectedDocId: string | null;
  onCitationClick: (citation: Citation) => void;
}

const SAMPLE_PROMPTS = [
  "What is the annual leave allocation and carryover policy?",
  "What is the reimbursement for home office and internet subsidy?",
  "How does the Cloud API authentication and bearer token work?",
  "What rate limit is enforced on the standard API tier?",
  "What was the Q3 ARR and revenue growth across business segments?",
];

export const ChatWindow: React.FC<ChatWindowProps> = ({ selectedDocId, onCitationClick }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Welcome to the Document Intelligence Assistant. Ask questions about your indexed documents, and I'll provide answers grounded strictly with verifiable citations [C1], [C2].",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || input).trim();
    if (!query || isLoading) return;

    setInput("");
    setError(null);

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: "user",
      content: query,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const history = messages
        .filter((m) => m.id !== "welcome")
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await sendChatMessage(query, history, selectedDocId || undefined);

      const assistantMessage: ChatMessage = {
        id: `asst_${Date.now()}`,
        role: "assistant",
        content: res.answer,
        citations: res.citations,
        provider: res.provider,
        model: res.model,
        chunks_used: res.chunks_used,
        validation_status: res.validation_status,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      setError(err.message || "Failed to generate answer");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Sparkles size={18} color="var(--accent-blue)" />
          <span style={{ fontWeight: 600, fontSize: "0.95rem" }}>
            Grounded Document Assistant
          </span>
          {selectedDocId && (
            <span style={{ fontSize: "0.75rem", padding: "2px 8px", background: "rgba(56, 189, 248, 0.15)", borderRadius: "4px", color: "var(--accent-blue)" }}>
              Filtered to selected document
            </span>
          )}
        </div>

        <button
          onClick={() => setMessages([messages[0]])}
          style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer", display: "flex", alignItems: "center", gap: "4px", fontSize: "0.75rem" }}
          title="Clear chat history"
        >
          <RefreshCw size={12} /> Reset Chat
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((m) => (
          <MessageItem key={m.id} message={m} onCitationClick={onCitationClick} />
        ))}

        {isLoading && (
          <div className="message-row assistant">
            <div className="message-avatar assistant">
              <Sparkles size={18} />
            </div>
            <div className="message-content" style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--text-secondary)" }}>
              <div className="status-dot" style={{ animation: "pulse 1s infinite" }} />
              Retrieving context, reranking passages, and validating citations...
            </div>
          </div>
        )}

        {error && (
          <div style={{ padding: "0.75rem 1rem", background: "rgba(239, 68, 68, 0.15)", border: "1px solid rgba(239, 68, 68, 0.3)", borderRadius: "8px", color: "#f87171", fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "8px" }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {messages.length <= 2 && !isLoading && (
          <div style={{ marginTop: "1rem" }}>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.5rem" }}>
              Suggested questions to try:
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
              {SAMPLE_PROMPTS.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(prompt)}
                  style={{
                    background: "rgba(30, 41, 59, 0.5)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "20px",
                    padding: "6px 12px",
                    color: "var(--text-secondary)",
                    fontSize: "0.78rem",
                    cursor: "pointer",
                    textAlign: "left",
                    transition: "all 0.2s",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = "var(--accent-blue)";
                    e.currentTarget.style.color = "var(--text-primary)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = "var(--border-color)";
                    e.currentTarget.style.color = "var(--text-secondary)";
                  }}
                >
                  "{prompt}"
                </button>
              ))}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <div className="chat-input-box">
          <textarea
            className="chat-textarea"
            rows={1}
            placeholder="Ask a question about your documents... (Press Enter to send)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            className="btn-send"
            disabled={!input.trim() || isLoading}
            onClick={() => handleSend()}
          >
            <Send size={16} />
            <span>Send</span>
          </button>
        </div>
      </div>
    </div>
  );
};
