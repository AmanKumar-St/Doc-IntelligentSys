import React, { useState, useRef, useEffect } from "react";
import { Send, Sparkles, AlertCircle, RefreshCw } from "lucide-react";
import type { ChatMessage, Citation, TaskType } from "../types";
import { MessageItem } from "./MessageItem";
import { TaskControls } from "./TaskControls";
import { executeTask } from "../api/client";

interface ChatWindowProps {
  selectedDocId: string | null;
  onCitationClick: (citation: Citation) => void;
}

const SAMPLE_PROMPTS = [
  "What is the annual leave allocation and carryover policy?",
  "Summarize the key leave and remote work benefits from the employee handbook.",
  "Extract the annual leave days, carryover limit, and sick leave days as JSON.",
  "Classify this document into HR Policy, Technical Spec, or Financial Report.",
  "Generate an executive briefing report summarizing financial results.",
];

export const ChatWindow: React.FC<ChatWindowProps> = ({ selectedDocId, onCitationClick }) => {
  const [selectedTask, setSelectedTask] = useState<TaskType>("qa");
  const [summaryType, setSummaryType] = useState<"concise" | "detailed" | "key_points">("detailed");
  const [targetFields, setTargetFields] = useState("annual_leave_days, carryover_limit, sick_leave_days");
  const [allowedCategories, setAllowedCategories] = useState("HR Policy, Technical Documentation, Financial Report, Other");
  const [outputFormat, setOutputFormat] = useState("report");

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Welcome to the AI-Powered Generative Content & Document Intelligence Platform. Select a task mode above (Ask Question, Summarize, Extract, Classify, Generate Content) and enter your instruction.",
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
      task_type: selectedTask,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const history = messages
        .filter((m) => m.id !== "welcome")
        .map((m) => ({ role: m.role, content: m.content }));

      const fieldsArray = targetFields ? targetFields.split(",").map((s) => s.trim()).filter(Boolean) : undefined;
      const catsArray = allowedCategories ? allowedCategories.split(",").map((s) => s.trim()).filter(Boolean) : undefined;

      const res = await executeTask({
        task_type: selectedTask,
        instruction: query,
        document_id: selectedDocId || undefined,
        history,
        summary_type: summaryType,
        target_fields: fieldsArray,
        allowed_categories: catsArray,
        output_format: outputFormat,
      });

      const assistantMessage: ChatMessage = {
        id: `asst_${Date.now()}`,
        role: "assistant",
        content: res.answer,
        task_type: res.task_type as TaskType,
        structured_data: res.structured_data,
        citations: res.citations,
        validation: res.validation,
        provider: res.provider,
        model: res.model,
        chunks_used: res.chunks_used,
        resolved_query: res.resolved_query,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      setError(err.message || "Failed to execute task");
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
            Generative Intelligence Studio
          </span>
          {selectedDocId && (
            <span style={{ fontSize: "0.75rem", padding: "2px 8px", background: "rgba(56, 189, 248, 0.15)", borderRadius: "4px", color: "var(--accent-blue)" }}>
              Filtered Document
            </span>
          )}
        </div>

        <button
          onClick={() => setMessages([messages[0]])}
          style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer", display: "flex", alignItems: "center", gap: "4px", fontSize: "0.75rem" }}
          title="Clear chat history"
        >
          <RefreshCw size={12} /> Reset Workspace
        </button>
      </div>

      {/* Task Controls Bar */}
      <TaskControls
        selectedTask={selectedTask}
        onSelectTask={setSelectedTask}
        summaryType={summaryType}
        setSummaryType={setSummaryType}
        targetFields={targetFields}
        setTargetFields={setTargetFields}
        allowedCategories={allowedCategories}
        setAllowedCategories={setAllowedCategories}
        outputFormat={outputFormat}
        setOutputFormat={setOutputFormat}
      />

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
              Executing {selectedTask.toUpperCase()} task, parsing context, and running validation...
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
              Suggested task prompts:
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
            placeholder={`Enter instruction for ${selectedTask.toUpperCase()} task... (Press Enter to execute)`}
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
            <span>Execute Task</span>
          </button>
        </div>
      </div>
    </div>
  );
};
