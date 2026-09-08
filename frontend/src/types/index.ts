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

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  provider?: string;
  model?: string;
  chunks_used?: number;
  timestamp: string;
  validation_status?: string;
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
