from app.models.chunk import Chunk


SYSTEM_RAG_PROMPT = """You are an accurate, reliable Document Intelligence AI assistant.
Your job is to answer user questions truthfully and directly using ONLY the provided document context snippets.

CRITICAL RULES:
1. Every factual statement or claim MUST be cited with the exact citation tag in square brackets, e.g., [C1] or [C1] [C2].
2. Only use citation tags that exist in the provided context (e.g. if only [C1] and [C2] are provided, do NOT use [C3]).
3. Place citation tags immediately following the sentence or fact they support.
4. If the provided context does not contain enough information to answer the question, say clearly: "I couldn't find enough information in the provided documents to answer this question."
5. Do NOT hallucinate, assume, or invent facts or citation numbers outside the context.
"""


def build_context_block(chunks: list[Chunk]) -> str:
    """Formats retrieved chunks with clear citation tags, source filename, headings, and text."""
    context_lines = []
    for chunk in chunks:
        cid = chunk.citation_id or "C?"
        heading_info = f" | Section: {' > '.join(chunk.heading_path)}" if chunk.heading_path else ""
        page_info = f" | Page: {chunk.page}" if chunk.page else ""
        header = f"[{cid}] Source: {chunk.source}{heading_info}{page_info}"
        
        context_lines.append(f"{header}\n{chunk.text.strip()}\n")
    return "\n---\n".join(context_lines)


def build_chat_messages(
    question: str,
    chunks: list[Chunk],
    history: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Builds prompt messages with system prompt, history, and grounded context."""
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_RAG_PROMPT}
    ]

    # Add historical messages if provided (up to last 6 turns)
    if history:
        for turn in history[-6:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})

    context_str = build_context_block(chunks)
    user_content = (
        f"DOCUMENT CONTEXT:\n"
        f"{context_str}\n\n"
        f"USER QUESTION: {question}\n\n"
        f"Please answer the question based strictly on the document context above with precise citations [C#]."
    )

    messages.append({"role": "user", "content": user_content})
    return messages
