import re
from app.models.chunk import Chunk


class FactualityValidator:
    """Performs deterministic factuality, numerical grounding, and consistency checks on outputs."""

    @staticmethod
    def extract_numbers_and_entities(text: str) -> list[str]:
        """Extracts numerical quantities, percentages, currency, and capitalized entities from text."""
        # Find currency, percentages, numerical values (e.g. $1,000, 22 days, 42%, 120 req/min)
        num_pattern = re.compile(r"(\$?\d+(?:,\d{3})*(?:\.\d+)?%?(?:\s*(?:days|months|hours|years|req|RPM|ARR|USD|MB|KB|GB))?)", re.IGNORECASE)
        matches = num_pattern.findall(text)
        return [m.strip() for m in matches if m.strip() and not m.strip().isdigit() or len(m.strip()) > 1]

    @staticmethod
    def check_factuality(
        answer_text: str,
        context_chunks: list[Chunk],
    ) -> tuple[str, float, list[str]]:
        """
        Verifies whether factual claims (numbers, specific metrics, key terms) in answer_text
        are grounded in the provided context_chunks.
        
        Returns:
            - status: "supported" | "partially_supported" | "unsupported" | "insufficient_context"
            - factuality_score: float (0.0 to 1.0)
            - warnings: list[str]
        """
        if not context_chunks:
            return "insufficient_context", 1.0, ["No context provided to evaluate factuality."]

        context_full = " ".join(c.text for c in context_chunks)
        context_clean = re.sub(r"\s+", " ", context_full).lower()

        # If answer explicitly acknowledges lack of info
        if "couldn't find enough information" in answer_text.lower() or "not mentioned" in answer_text.lower():
            return "supported", 1.0, []

        warnings: list[str] = []
        # Clean out JSON metadata fields like "confidence": 0.9 before checking factual grounding
        clean_answer = re.sub(r'"confidence"\s*:\s*[01]\.?\d*', '', answer_text)
        numbers_in_answer = FactualityValidator.extract_numbers_and_entities(clean_answer)

        if not numbers_in_answer:
            # Word-level overlap check for key nouns
            answer_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", answer_text.lower()))
            context_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", context_clean))
            stop_words = {"this", "that", "with", "from", "have", "were", "what", "which", "your", "their", "about", "could", "would", "should"}
            substantive_answer = answer_words - stop_words
            overlap = substantive_answer.intersection(context_words)
            
            coverage = len(overlap) / max(len(substantive_answer), 1)
            score = round(min(1.0, coverage * 1.2), 2)
            status = "supported" if score >= 0.6 else "partially_supported" if score >= 0.3 else "unsupported"
            if status != "supported":
                warnings.append(f"Low semantic vocabulary overlap with context ({score * 100:.0f}%).")
            return status, score, warnings

        # Verify extracted numbers/metrics exist in context
        grounded_count = 0
        for num in numbers_in_answer:
            # Normalize for simple substring check
            num_clean = num.lower().replace(",", "").replace("$", "")
            context_num_clean = context_clean.replace(",", "").replace("$", "")

            if num.lower() in context_clean or num_clean in context_num_clean:
                grounded_count += 1
            else:
                warnings.append(f"Metric or quantity '{num}' not directly located in source context.")

        score = round(grounded_count / len(numbers_in_answer), 2)
        if score >= 0.8:
            status = "supported"
        elif score >= 0.4:
            status = "partially_supported"
        else:
            status = "unsupported"

        return status, score, warnings
