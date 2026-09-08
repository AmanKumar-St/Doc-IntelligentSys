from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field
from app.schemas.chat import ChatCitation, ChatMessage


class TaskType(str, Enum):
    QA = "qa"
    SUMMARIZATION = "summarization"
    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    GENERATION = "generation"


class TaskRequest(BaseModel):
    task_type: TaskType = Field(default=TaskType.QA, description="Generative task mode")
    instruction: str = Field(..., min_length=1, description="User instruction, prompt, or question")
    document_id: str | None = Field(default=None, description="Optional document filter")
    history: list[ChatMessage] = Field(default_factory=list, description="Previous conversation turns")
    
    # Task-specific parameters
    summary_type: Literal["concise", "detailed", "key_points"] = Field(
        default="detailed", description="Summarization format style"
    )
    target_fields: list[str] | None = Field(
        default=None, description="List of fields to extract in extraction mode"
    )
    allowed_categories: list[str] | None = Field(
        default=None, description="Allowed category list for classification"
    )
    output_format: str = Field(
        default="report", description="Target deliverable format for content generation"
    )
    model_override: str | None = Field(
        default=None, description="Optional model override"
    )


class ValidationReportSchema(BaseModel):
    status: str
    structure_valid: bool
    citation_valid: bool
    factuality_status: str
    factuality_score: float
    warnings: list[str] = []
    extracted_data: dict[str, Any] | None = None


class TaskResponse(BaseModel):
    task_type: TaskType
    answer: str
    structured_data: dict[str, Any] | None = None
    citations: list[ChatCitation]
    validation: ValidationReportSchema
    provider: str
    model: str
    chunks_used: int
    resolved_query: str | None = None
