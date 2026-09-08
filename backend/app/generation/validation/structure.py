import json
import re
from typing import Any


class StructureValidator:
    """Validates structural correctness of model outputs (JSON, categories, required fields)."""

    @staticmethod
    def extract_and_parse_json(text: str) -> tuple[dict[str, Any] | None, str | None]:
        """
        Safely extracts and parses JSON from raw LLM text (handling markdown fences, whitespace).
        Returns: (parsed_dict, error_message)
        """
        if not text or not text.strip():
            return None, "Empty output received"

        clean_text = text.strip()

        # Check for ```json ... ``` blocks
        json_fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text)
        if json_fence_match:
            candidate = json_fence_match.group(1).strip()
        else:
            # Look for outer brackets { ... }
            first_brace = clean_text.find("{")
            last_brace = clean_text.rfind("}")
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                candidate = clean_text[first_brace : last_brace + 1].strip()
            else:
                candidate = clean_text

        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed, None
            return None, "Parsed JSON is not an object/dictionary"
        except json.JSONDecodeError as e:
            return None, f"JSON parse error: {str(e)}"

    @staticmethod
    def validate_classification(
        output_dict: dict[str, Any] | None,
        raw_text: str,
        allowed_categories: list[str],
    ) -> tuple[str, float, str, list[str]]:
        """
        Validates that a classification result matches one of the allowed categories.
        Returns: (matched_category, confidence, explanation, warnings)
        """
        warnings: list[str] = []
        category = "Uncategorized"
        confidence = 0.5
        explanation = ""

        if output_dict and "category" in output_dict:
            raw_cat = str(output_dict.get("category", "")).strip()
            confidence = float(output_dict.get("confidence", 0.8))
            explanation = str(output_dict.get("explanation", ""))
        else:
            raw_cat = raw_text.strip()
            explanation = raw_text

        # Match against allowed categories (case-insensitive fuzzy match)
        matched = None
        for allowed in allowed_categories:
            if allowed.lower() == raw_cat.lower():
                matched = allowed
                break
        
        if not matched:
            # Substring search match
            for allowed in allowed_categories:
                if allowed.lower() in raw_cat.lower() or raw_cat.lower() in allowed.lower():
                    matched = allowed
                    break

        if matched:
            category = matched
        else:
            # If "Other" exists in allowed categories, default to Other, else pick first with warning
            if "Other" in allowed_categories:
                category = "Other"
            elif "Uncategorized" in allowed_categories:
                category = "Uncategorized"
            elif allowed_categories:
                category = allowed_categories[0]
            warnings.append(
                f"Model category '{raw_cat}' did not strictly match allowed list {allowed_categories}. Coerced to '{category}'."
            )

        return category, max(0.0, min(1.0, confidence)), explanation, warnings

    @staticmethod
    def validate_required_fields(
        data: dict[str, Any],
        required_fields: list[str],
    ) -> list[str]:
        """Checks for missing required fields in extracted dictionary."""
        missing = []
        for f in required_fields:
            if f not in data:
                missing.append(f)
        return missing
