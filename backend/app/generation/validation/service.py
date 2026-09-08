from dataclasses import dataclass, field
from typing import Any
from app.models.chunk import Chunk
from app.models.citation import Citation
from app.generation.validation.citation import CitationValidator
from app.generation.validation.structure import StructureValidator
from app.generation.validation.factuality import FactualityValidator


@dataclass
class ValidationReport:
    status: str  # "valid" | "cleaned_invalid" | "partial" | "invalid"
    structure_valid: bool
    citation_valid: bool
    factuality_status: str  # "supported" | "partially_supported" | "unsupported" | "insufficient_context"
    factuality_score: float
    warnings: list[str] = field(default_factory=list)
    extracted_data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "structure_valid": self.structure_valid,
            "citation_valid": self.citation_valid,
            "factuality_status": self.factuality_status,
            "factuality_score": self.factuality_score,
            "warnings": self.warnings,
            "extracted_data": self.extracted_data,
        }


class ValidationService:
    """Unified validation service performing structure, citation, and factuality checks."""

    @staticmethod
    def validate_task_output(
        task_type: str,
        raw_output: str,
        context_chunks: list[Chunk],
        target_fields: list[str] | None = None,
        allowed_categories: list[str] | None = None,
    ) -> tuple[str, list[Citation], ValidationReport]:
        warnings: list[str] = []
        extracted_dict: dict[str, Any] | None = None
        structure_valid = True

        # 1. Structure / Format Validation
        if task_type in ["extraction", "classification"]:
            parsed_json, json_err = StructureValidator.extract_and_parse_json(raw_output)
            if json_err:
                structure_valid = False
                warnings.append(f"Structure issue: {json_err}")
            else:
                extracted_dict = parsed_json

            if task_type == "classification" and allowed_categories:
                cat, conf, expl, cat_warns = StructureValidator.validate_classification(
                    extracted_dict, raw_output, allowed_categories
                )
                warnings.extend(cat_warns)
                if not extracted_dict:
                    extracted_dict = {
                        "category": cat,
                        "confidence": conf,
                        "explanation": expl,
                    }
                else:
                    extracted_dict["category"] = cat

            elif task_type == "extraction" and target_fields and extracted_dict:
                missing = StructureValidator.validate_required_fields(extracted_dict, target_fields)
                if missing:
                    warnings.append(f"Missing fields in extraction: {missing}")

        # 2. Citation Validation
        cleaned_text, citations, cit_status = CitationValidator.validate_and_map_citations(
            answer_text=raw_output,
            context_chunks=context_chunks,
            strict=False,
        )
        citation_valid = cit_status in ["valid", "unverified"]
        if cit_status == "cleaned_invalid":
            warnings.append("Filtered unsupported citation tags.")

        # 3. Factuality Checking
        fact_status, fact_score, fact_warns = FactualityValidator.check_factuality(
            answer_text=cleaned_text,
            context_chunks=context_chunks,
        )
        warnings.extend(fact_warns)

        # Overall Status Determination
        if structure_valid and citation_valid and fact_status in ["supported", "insufficient_context"]:
            overall_status = "valid"
        elif cit_status == "cleaned_invalid" or fact_status == "partially_supported":
            overall_status = "partial"
        else:
            overall_status = "invalid" if not structure_valid else "valid"

        report = ValidationReport(
            status=overall_status,
            structure_valid=structure_valid,
            citation_valid=citation_valid,
            factuality_status=fact_status,
            factuality_score=fact_score,
            warnings=warnings,
            extracted_data=extracted_dict,
        )

        return cleaned_text, citations, report
