from app.models.chunk import Chunk


SYSTEM_CLASSIFICATION_PROMPT = """You are a rigorous document classification system.
Your job is to classify the provided document context into EXACTLY ONE category from the user-provided allowed categories list.

CRITICAL CLASSIFICATION RULES:
1. You MUST choose ONLY from the provided allowed categories list. Never invent, alter, or create new category names.
2. Return your response as a strict JSON object with the following schema:
{
  "category": "<Exact Category From Allowed List>",
  "confidence": <float between 0.0 and 1.0>,
  "explanation": "<Brief explanation citing document evidence>",
  "citations": ["C1", "C2"]
}
3. If the context does not clearly match any specific category and "Other" or "Uncategorized" is in the allowed list, select that.
"""


def build_classification_messages(
    instruction: str,
    chunks: list[Chunk],
    categories: list[str],
    history: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_CLASSIFICATION_PROMPT}]

    context_lines = []
    for chunk in chunks:
        cid = chunk.citation_id or "C?"
        heading_info = f" | Section: {' > '.join(chunk.heading_path)}" if chunk.heading_path else ""
        context_lines.append(f"[{cid}] Source: {chunk.source}{heading_info}\n{chunk.text.strip()}\n")
    
    context_str = "\n---\n".join(context_lines)
    categories_str = ", ".join(f'"{c}"' for c in categories)

    user_content = (
        f"DOCUMENT CONTEXT:\n{context_str}\n\n"
        f"ALLOWED CATEGORIES LIST:\n[{categories_str}]\n\n"
        f"CLASSIFICATION INSTRUCTION: {instruction or 'Classify this document context into the single best matching category.'}\n\n"
        f"Return ONLY a valid JSON object matching the requested schema."
    )
    messages.append({"role": "user", "content": user_content})
    return messages
