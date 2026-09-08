import pytest
from app.models.chunk import Chunk
from app.generation.validation.structure import StructureValidator
from app.generation.validation.factuality import FactualityValidator
from app.generation.validation import ValidationService


def test_extract_and_parse_json_valid():
    raw = '```json\n{"annual_leave": 22, "carryover": 5, "_citations": ["C1"]}\n```'
    parsed, err = StructureValidator.extract_and_parse_json(raw)
    assert err is None
    assert parsed == {"annual_leave": 22, "carryover": 5, "_citations": ["C1"]}


def test_extract_and_parse_json_embedded():
    raw = 'Here is the extracted data: {"status": "success", "count": 10}. Hope this helps!'
    parsed, err = StructureValidator.extract_and_parse_json(raw)
    assert err is None
    assert parsed == {"status": "success", "count": 10}


def test_extract_and_parse_json_invalid():
    raw = "Not a json document at all"
    parsed, err = StructureValidator.extract_and_parse_json(raw)
    assert err is not None
    assert parsed is None


def test_validate_classification_allowed():
    allowed = ["HR Policy", "Technical Documentation", "Financial Report"]
    raw_dict = {"category": "hr policy", "confidence": 0.95, "explanation": "Discusses leave and vacation."}
    cat, conf, expl, warns = StructureValidator.validate_classification(raw_dict, "", allowed)
    assert cat == "HR Policy"
    assert conf == 0.95
    assert len(warns) == 0


def test_validate_classification_unauthorized_category():
    allowed = ["Technical Documentation", "Financial Report", "Other"]
    raw_dict = {"category": "Medical Research", "confidence": 0.9}
    cat, conf, expl, warns = StructureValidator.validate_classification(raw_dict, "", allowed)
    assert cat == "Other"
    assert len(warns) > 0


def test_validate_required_fields():
    data = {"name": "Alice", "role": "Engineer"}
    missing = StructureValidator.validate_required_fields(data, ["name", "role", "salary"])
    assert missing == ["salary"]


def test_factuality_validator_numerical_grounded():
    chunks = [
        Chunk(id="1", document_id="d1", text="Employees are granted 22 days of annual leave and $80 monthly stipend.", source="s.docx", citation_id="C1")
    ]
    answer = "Employees receive 22 days of leave [C1] and $80 per month."
    status, score, warns = FactualityValidator.check_factuality(answer, chunks)
    assert status == "supported"
    assert score >= 0.8


def test_factuality_validator_numerical_hallucinated():
    chunks = [
        Chunk(id="1", document_id="d1", text="Employees are granted 22 days of annual leave.", source="s.docx", citation_id="C1")
    ]
    # $500 and 60 days are not in context
    answer = "Employees receive 60 days of annual leave with a $500 monthly stipend."
    status, score, warns = FactualityValidator.check_factuality(answer, chunks)
    assert status == "unsupported"
    assert len(warns) > 0


def test_unified_validation_service():
    chunks = [
        Chunk(id="1", document_id="d1", text="Standard working hours are 40 hours per week.", source="handbook.docx", citation_id="C1")
    ]
    raw_output = "Standard working hours are 40 hours per week [C1]."
    cleaned, citations, report = ValidationService.validate_task_output(
        task_type="qa",
        raw_output=raw_output,
        context_chunks=chunks,
    )
    assert report.status == "valid"
    assert report.structure_valid is True
    assert report.citation_valid is True
    assert report.factuality_status == "supported"
    assert len(citations) == 1
