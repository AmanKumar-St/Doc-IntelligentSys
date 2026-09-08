export type TaskType = "qa" | "summarization" | "extraction" | "classification" | "generation";

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  size_bytes: number;
  chunk_count: number;
  created_at: string;
  status: "uploaded" | "parsing" | "chunking" | "embedded" | "error";
  error_message?: string;
}

export interface Citation {
  id: string;
  chunk_id: string;
  document_id: string;
  source: string;
  section?: string;
  page?: number;
  heading_path: string[];
  snippet: string;
  score?: number;
}

export interface ValidationReport {
  status: string;
  structure_valid: boolean;
  citation_valid: boolean;
  factuality_status: string;
  factuality_score: number;
  warnings: string[];
  extracted_data?: Record<string, any> | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  task_type?: TaskType;
  structured_data?: Record<string, any> | null;
  citations?: Citation[];
  validation?: ValidationReport;
  provider?: string;
  model?: string;
  chunks_used?: number;
  timestamp: string;
  resolved_query?: string | null;
}

export interface TaskRequestParams {
  task_type: TaskType;
  instruction: string;
  document_id?: string | null;
  history?: { role: string; content: string }[];
  summary_type?: "concise" | "detailed" | "key_points";
  target_fields?: string[];
  allowed_categories?: string[];
  output_format?: string;
  model_override?: string | null;
}

export interface SearchResult {
  citation_id: string;
  chunk_id: string;
  document_id: string;
  source: string;
  text: string;
  section?: string;
  page?: number;
  heading_path: string[];
  score: number;
}

export interface SystemHealth {
  status: string;
  app_name: string;
  environment: string;
  embedding_provider: string;
  generation_provider: string;
  reranker_provider: string;
  storage_mode: string;
}
