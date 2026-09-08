from app.models.chunk import Chunk


SYSTEM_QA_PROMPT = """You are an accurate, reliable Document Intelligence AI assistant.
Your job is to answer user questions truthfully and directly using ONLY the provided document context snippets.

CRITICAL RULES:
1. Every factual statement or claim MUST be cited with the exact citation tag in square brackets, e.g., [C1] or [C1] [C2].
2. Only use citation tags that exist in the provided context. Do NOT invent citation tags.
3. Place citation tags immediately following the sentence or fact they support.
4. If the provided context does not contain enough information to answer the question, state: "I couldn't find enough information in the provided documents to answer this question."
5. Do NOT hallucinate, assume, or invent facts or citation numbers outside the context.
"""


def build_qa_messages(
    question: str,
    chunks: list[Chunk],
    history: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    from app.generation.prompts.qa import SYSTEM_QA_PROMPT
    
    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_QA_PROMPT}]

    if history:
        for turn in history[-6:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})

    context_lines = []
    for chunk in chunks:
        cid = chunk.citation_id or "C?"
        heading_info = f" | Section: {' > '.join(chunk.heading_path)}" if chunk.heading_path else ""
        page_info = f" | Page: {chunk.page}" if chunk.page else ""
        header = f"[{cid}] Source: {chunk.source}{heading_info}{page_info}"
        context_lines.append(f"{header}\n{chunk.text.strip()}\n")
    
    context_str = "\n---\n".join(context_lines)
    user_content = (
        f"DOCUMENT CONTEXT:\n{context_str}\n\n"
        f"USER QUESTION: {question}\n\n"
        f"Please answer strictly based on the document context with precise citations [C#]."
    )
    messages.append({"role": "user", "content": user_content})
    return messages
