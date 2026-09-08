import json
from app.models.chunk import Chunk


SYSTEM_EXTRACTION_PROMPT = """You are a high-precision structured data extraction engine.
Your task is to extract specific entities and fields from the provided document context into strict, valid JSON.

CRITICAL EXTRACTION RULES:
1. Extract values EXACTLY as stated in the document context.
2. Return ONLY a valid JSON object matching the requested schema. No markdown fences around it if possible, or standard ```json block.
3. If a requested field is NOT found in the context, set its value explicitly to null. DO NOT fabricate, guess, or assume missing data.
4. Include a "_citations" array field listing the citation IDs (e.g. ["C1", "C2"]) supporting the extracted facts.
5. Include a "_confidence" field (0.0 to 1.0) reflecting extraction completeness.
"""


def build_extraction_messages(
    instruction: str,
    chunks: list[Chunk],
    fields: list[str] | None = None,
    history: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_EXTRACTION_PROMPT}]

    context_lines = []
    for chunk in chunks:
        cid = chunk.citation_id or "C?"
        heading_info = f" | Section: {' > '.join(chunk.heading_path)}" if chunk.heading_path else ""
        context_lines.append(f"[{cid}] Source: {chunk.source}{heading_info}\n{chunk.text.strip()}\n")
    
    context_str = "\n---\n".join(context_lines)

    target_fields_str = f"Target Fields to Extract: {', '.join(fields)}" if fields else "Extract all key factual entities and attributes."

    user_content = (
        f"DOCUMENT CONTEXT:\n{context_str}\n\n"
        f"EXTRACTION TASK: {instruction}\n"
        f"{target_fields_str}\n\n"
        f"Output JSON schema format:\n"
        f"{{\n"
        f'  "<field_name>": "<extracted_value_or_null>",\n'
        f'  "_citations": ["C1"],\n'
        f'  "_confidence": 1.0\n'
        f"}}\n"
        f"Return ONLY valid JSON."
    )
    messages.append({"role": "user", "content": user_content})
    return messages
