import pytest
from app.models.chunk import Chunk
from app.generation.prompts import (
    build_qa_messages,
    build_summarization_messages,
    build_extraction_messages,
    build_classification_messages,
    build_content_generation_messages,
)


@pytest.fixture
def sample_chunks():
    return [
        Chunk(
            id="c1",
            document_id="doc_1",
            text="Employees get 22 days of annual leave and can carry forward up to 5 days.",
            source="handbook.docx",
            citation_id="C1",
            heading_path=["Company Policy", "Leave"],
            page=1,
        ),
        Chunk(
            id="c2",
            document_id="doc_1",
            text="Remote employees receive $80 monthly internet subsidy via automated payroll.",
            source="handbook.docx",
            citation_id="C2",
            heading_path=["Company Policy", "Remote Work"],
            page=2,
        ),
    ]


def test_build_qa_messages(sample_chunks):
    messages = build_qa_messages("What is the leave policy?", sample_chunks)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "[C1]" in messages[1]["content"]
    assert "What is the leave policy?" in messages[1]["content"]


def test_build_summarization_messages(sample_chunks):
    messages = build_summarization_messages("Summarize benefits", sample_chunks, summary_type="key_points")
    assert len(messages) == 2
    assert "KEY_POINTS" in messages[1]["content"]
    assert "[C2]" in messages[1]["content"]


def test_build_extraction_messages(sample_chunks):
    fields = ["annual_leave", "internet_subsidy"]
    messages = build_extraction_messages("Extract benefits data", sample_chunks, fields=fields)
    assert len(messages) == 2
    assert "annual_leave, internet_subsidy" in messages[1]["content"]
    assert "Return ONLY valid JSON" in messages[1]["content"]


def test_build_classification_messages(sample_chunks):
    cats = ["HR Policy", "Technical Spec", "Financials"]
    messages = build_classification_messages("Classify this document", sample_chunks, categories=cats)
    assert len(messages) == 2
    assert '"HR Policy"' in messages[1]["content"]
    assert "confidence" in messages[0]["content"]


def test_build_content_generation_messages(sample_chunks):
    messages = build_content_generation_messages(
        user_requirement="Write an onboarding email for new hires",
        chunks=sample_chunks,
        output_format="email",
    )
    assert len(messages) == 2
    assert "AUTHORITATIVE SOURCE DOCUMENT CONTEXT" in messages[1]["content"]
    assert "USER REQUIREMENTS" in messages[1]["content"]
    assert "EMAIL" in messages[1]["content"]
