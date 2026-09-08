import pytest
from app.generation.validation import CitationValidator
from app.models.chunk import Chunk
from app.core.exceptions import CitationValidationError


def test_extract_citations():
    text = "Employees receive 18 days leave [C1] and carry forward 5 days [C2]. Bonus details [C10]."
    extracted = CitationValidator.extract_citation_ids(text)
    assert extracted == {"C1", "C2", "C10"}


def test_validate_citations_valid():
    chunks = [
        Chunk(id="c1", document_id="doc1", text="18 days leave", source="handbook.pdf", citation_id="C1"),
        Chunk(id="c2", document_id="doc1", text="5 days carryover", source="handbook.pdf", citation_id="C2"),
    ]
    answer = "Employees get 18 days leave [C1] and can carry over 5 days [C2]."
    cleaned, citations, status = CitationValidator.validate_and_map_citations(answer, chunks)
    
    assert status == "valid"
    assert len(citations) == 2
    assert citations[0].id == "C1"
    assert citations[0].source == "handbook.pdf"
    assert citations[1].id == "C2"


def test_validate_citations_invalid_hallucinated():
    chunks = [
        Chunk(id="c1", document_id="doc1", text="18 days leave", source="handbook.pdf", citation_id="C1"),
    ]
    answer = "Employees get 18 days [C1] and unlimited sick leave [C9]."
    
    # Non-strict mode should remove [C9] and return cleaned_invalid status
    cleaned, citations, status = CitationValidator.validate_and_map_citations(answer, chunks, strict=False)
    assert status == "cleaned_invalid"
    assert "[C9]" not in cleaned
    assert len(citations) == 1
    assert citations[0].id == "C1"

    # Strict mode should raise CitationValidationError
    with pytest.raises(CitationValidationError):
        CitationValidator.validate_and_map_citations(answer, chunks, strict=True)
