import pytest
from app.ingestion.chunker import MarkdownChunker


def test_markdown_chunker_basic_headings():
    chunker = MarkdownChunker(chunk_size=500, chunk_overlap=50)
    markdown_doc = """# Company Policy
Welcome to the company policy guide.

## Leave Policy
Employees receive 20 days of annual paid leave per fiscal year.
Sick leave is allocated at 10 days per year.

### Carry Forward
Up to 5 unused annual leave days can be carried forward to the next year.

## Benefits
Health insurance covers 100% of preventive care.
"""
    chunks = chunker.chunk_document(markdown_doc, document_id="doc_test_1", source="policy.md")
    
    assert len(chunks) >= 3
    # Check that chunks preserve section headers and heading paths
    leave_chunks = [c for c in chunks if "Leave Policy" in (c.section or "")]
    assert len(leave_chunks) > 0
    assert any("Company Policy" in c.heading_path for c in leave_chunks)
    
    carry_chunks = [c for c in chunks if "Carry Forward" in (c.section or "")]
    assert len(carry_chunks) > 0
    assert any("Carry Forward" in c.heading_path for c in carry_chunks)


def test_markdown_chunker_large_block():
    chunker = MarkdownChunker(chunk_size=200, chunk_overlap=50)
    long_paragraph = "This is a detailed paragraph explaining complex regulatory compliance requirements. " * 10
    doc = f"# Compliance\n\n{long_paragraph}"
    
    chunks = chunker.chunk_document(doc, document_id="doc_test_2", source="compliance.md")
    assert len(chunks) > 1
    for c in chunks:
        assert c.document_id == "doc_test_2"
        assert c.heading_path == ["Compliance"]
        assert len(c.text) > 0
