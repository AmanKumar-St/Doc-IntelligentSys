import React from "react";
import { MessageSquare, AlignLeft, FileSearch, Tag, FileText } from "lucide-react";
import type { TaskType } from "../types";

interface TaskControlsProps {
  selectedTask: TaskType;
  onSelectTask: (task: TaskType) => void;
  summaryType: "concise" | "detailed" | "key_points";
  setSummaryType: (val: "concise" | "detailed" | "key_points") => void;
  targetFields: string;
  setTargetFields: (val: string) => void;
  allowedCategories: string;
  setAllowedCategories: (val: string) => void;
  outputFormat: string;
  setOutputFormat: (val: string) => void;
}

export const TaskControls: React.FC<TaskControlsProps> = ({
  selectedTask,
  onSelectTask,
  summaryType,
  setSummaryType,
  targetFields,
  setTargetFields,
  allowedCategories,
  setAllowedCategories,
  outputFormat,
  setOutputFormat,
}) => {
  const tasks: { type: TaskType; label: string; icon: React.ReactNode }[] = [
    { type: "qa", label: "Ask Question", icon: <MessageSquare size={14} /> },
    { type: "summarization", label: "Summarize", icon: <AlignLeft size={14} /> },
    { type: "extraction", label: "Extract JSON", icon: <FileSearch size={14} /> },
    { type: "classification", label: "Classify", icon: <Tag size={14} /> },
    { type: "generation", label: "Generate Content", icon: <FileText size={14} /> },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.65rem", padding: "0.75rem 1rem", background: "rgba(15, 23, 42, 0.6)", borderBottom: "1px solid var(--border-color)" }}>
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        {tasks.map((t) => {
          const isActive = selectedTask === t.type;
          return (
            <button
              key={t.type}
              onClick={() => onSelectTask(t.type)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "5px",
                padding: "5px 12px",
                borderRadius: "20px",
                border: "1px solid",
                borderColor: isActive ? "var(--accent-blue)" : "var(--border-color)",
                background: isActive ? "rgba(56, 189, 248, 0.15)" : "rgba(30, 41, 59, 0.4)",
                color: isActive ? "var(--accent-blue)" : "var(--text-secondary)",
                fontSize: "0.8rem",
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.2s",
              }}
            >
              {t.icon}
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Task-Specific Parameter Inputs */}
      {selectedTask === "summarization" && (
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", fontSize: "0.78rem" }}>
          <span style={{ color: "var(--text-muted)" }}>Summary Style:</span>
          {(["detailed", "concise", "key_points"] as const).map((style) => (
            <label key={style} style={{ display: "flex", alignItems: "center", gap: "4px", cursor: "pointer", color: summaryType === style ? "var(--accent-blue)" : "var(--text-secondary)" }}>
              <input
                type="radio"
                name="summary_style"
                checked={summaryType === style}
                onChange={() => setSummaryType(style)}
              />
              {style.replace("_", " ").toUpperCase()}
            </label>
          ))}
        </div>
      )}

      {selectedTask === "extraction" && (
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.78rem" }}>
          <span style={{ color: "var(--text-muted)", flexShrink: 0 }}>Target Fields:</span>
          <input
            type="text"
            placeholder="e.g. employee_name, annual_leave_days, salary"
            value={targetFields}
            onChange={(e) => setTargetFields(e.target.value)}
            style={{
              flex: 1,
              background: "var(--bg-input)",
              border: "1px solid var(--border-color)",
              borderRadius: "6px",
              padding: "4px 8px",
              color: "var(--text-primary)",
              fontSize: "0.78rem",
              outline: "none",
            }}
          />
        </div>
      )}

      {selectedTask === "classification" && (
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.78rem" }}>
          <span style={{ color: "var(--text-muted)", flexShrink: 0 }}>Allowed Categories:</span>
          <input
            type="text"
            placeholder="e.g. HR Policy, Technical Documentation, Financial Report, Other"
            value={allowedCategories}
            onChange={(e) => setAllowedCategories(e.target.value)}
            style={{
              flex: 1,
              background: "var(--bg-input)",
              border: "1px solid var(--border-color)",
              borderRadius: "6px",
              padding: "4px 8px",
              color: "var(--text-primary)",
              fontSize: "0.78rem",
              outline: "none",
            }}
          />
        </div>
      )}

      {selectedTask === "generation" && (
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", fontSize: "0.78rem" }}>
          <span style={{ color: "var(--text-muted)" }}>Target Deliverable Format:</span>
          <select
            value={outputFormat}
            onChange={(e) => setOutputFormat(e.target.value)}
            style={{
              background: "var(--bg-input)",
              border: "1px solid var(--border-color)",
              borderRadius: "6px",
              padding: "4px 8px",
              color: "var(--text-primary)",
              fontSize: "0.78rem",
            }}
          >
            <option value="report">Structured Report</option>
            <option value="email">Executive Email</option>
            <option value="technical_memo">Technical Memo</option>
            <option value="policy_summary">Policy Briefing</option>
          </select>
        </div>
      )}
    </div>
  );
};
