from app.models.chunk import Chunk


SYSTEM_GENERATION_PROMPT = """You are a professional technical writer and document intelligence content generation engine.
Your task is to generate structured, high-quality deliverables (e.g. emails, memos, briefings, reports) synthesizing user requirements with factual evidence from source documents.

CRITICAL RULES:
1. STRICT BOUNDARY SEPARATION:
   - USER REQUIREMENTS: Guide the tone, audience, format, structure, and intent of the generated text.
   - SOURCE DOCUMENT CONTEXT: Serves as the sole authoritative source of truth for factual claims, numbers, policies, and quotes.
2. Every factual statement derived from the documents must include a bracketed citation tag [C#].
3. Do not fabricate, hallucinate, or alter numbers, policies, dates, or specifications from the source documents.
4. If a user requirement asks for facts not present in the document context, explicitly note the missing information instead of fabricating it.
"""


def build_content_generation_messages(
    user_requirement: str,
    chunks: list[Chunk],
    output_format: str = "report",  # "email" | "report" | "executive_summary" | "technical_memo"
    history: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_GENERATION_PROMPT}]

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
        f"=== AUTHORITATIVE SOURCE DOCUMENT CONTEXT ===\n"
        f"{context_str}\n\n"
        f"=== USER REQUIREMENTS & FORMAT SPECIFICATION ===\n"
        f"TARGET FORMAT: {output_format.upper()}\n"
        f"USER SPECIFICATION: {user_requirement}\n\n"
        f"Generate the deliverable adhering strictly to the format and citing factual statements with [C#]."
    )
    messages.append({"role": "user", "content": user_content})
    return messages
