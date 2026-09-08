from app.models.chunk import Chunk


SYSTEM_SUMMARIZATION_PROMPT = """You are an expert executive summarizer and Document Intelligence assistant.
Your task is to produce clear, well-structured summaries of the provided document context based on the user's instructions.

CRITICAL RULES:
1. Base the summary EXCLUSIVELY on the provided document context.
2. Do not introduce outside knowledge, unverified assumptions, or hallucinations.
3. Every key finding, bullet point, or section must include relevant bracketed citations (e.g. [C1], [C2]).
4. Structure the summary cleanly with bullet points, numbered key takeaways, or paragraphs as requested.
5. If the document does not contain sufficient details for a requested aspect, explicitly state that.
"""


def build_summarization_messages(
    instruction: str,
    chunks: list[Chunk],
    summary_type: str = "detailed",  # "concise" | "detailed" | "key_points"
    history: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_SUMMARIZATION_PROMPT}]

    if history:
        for turn in history[-4:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})

    context_lines = []
    for chunk in chunks:
        cid = chunk.citation_id or "C?"
        heading_info = f" | Section: {' > '.join(chunk.heading_path)}" if chunk.heading_path else ""
        context_lines.append(f"[{cid}] Source: {chunk.source}{heading_info}\n{chunk.text.strip()}\n")
    
    context_str = "\n---\n".join(context_lines)

    user_content = (
        f"DOCUMENT CONTEXT:\n{context_str}\n\n"
        f"SUMMARY FORMAT DESIRED: {summary_type.upper()}\n"
        f"USER INSTRUCTION: {instruction or 'Summarize the core topics, policies, and findings from the provided document.'}\n\n"
        f"Provide a structured summary with inline citations [C#] for every claim."
    )
    messages.append({"role": "user", "content": user_content})
    return messages
