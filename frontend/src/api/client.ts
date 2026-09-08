import type { DocumentItem, SearchResult, SystemHealth } from "../types";

const API_BASE = "http://localhost:8000/api";

export async function checkHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function fetchDocuments(): Promise<DocumentItem[]> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error("Failed to fetch documents");
  const data = await res.json();
  return data.documents;
}

export async function uploadDocument(file: File): Promise<{ document_id: string; message: string; chunk_count: number }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/documents`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function deleteDocument(documentId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete document");
}

export async function sendChatMessage(
  question: string,
  history: { role: string; content: string }[] = [],
  documentId?: string
): Promise<{
  answer: string;
  citations: any[];
  provider: string;
  model: string;
  chunks_used: number;
  validation_status: string;
}> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      history,
      document_id: documentId || null,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Chat request failed" }));
    throw new Error(err.detail || "Chat request failed");
  }
  return res.json();
}

export async function semanticSearch(query: string, topK: number = 6, documentId?: string): Promise<SearchResult[]> {
  const res = await fetch(`${API_BASE}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      top_k: topK,
      document_id: documentId || null,
    }),
  });

  if (!res.ok) throw new Error("Search failed");
  const data = await res.json();
  return data.results;
}
