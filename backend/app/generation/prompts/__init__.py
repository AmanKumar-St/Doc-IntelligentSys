from app.generation.prompts.qa import build_qa_messages, SYSTEM_QA_PROMPT
from app.generation.prompts.summarization import build_summarization_messages, SYSTEM_SUMMARIZATION_PROMPT
from app.generation.prompts.extraction import build_extraction_messages, SYSTEM_EXTRACTION_PROMPT
from app.generation.prompts.classification import build_classification_messages, SYSTEM_CLASSIFICATION_PROMPT
from app.generation.prompts.generation import build_content_generation_messages, SYSTEM_GENERATION_PROMPT

# Backward compatibility alias
build_chat_messages = build_qa_messages

__all__ = [
    "build_qa_messages",
    "build_chat_messages",
    "SYSTEM_QA_PROMPT",
    "build_summarization_messages",
    "SYSTEM_SUMMARIZATION_PROMPT",
    "build_extraction_messages",
    "SYSTEM_EXTRACTION_PROMPT",
    "build_classification_messages",
    "SYSTEM_CLASSIFICATION_PROMPT",
    "build_content_generation_messages",
    "SYSTEM_GENERATION_PROMPT",
]
