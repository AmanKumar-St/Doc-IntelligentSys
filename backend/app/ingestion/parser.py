from pathlib import Path
from markitdown import MarkItDown
from app.core.exceptions import DocumentParsingError
from app.core.logging import logger


class DocumentParser:
    def __init__(self) -> None:
        self.converter = MarkItDown()

    def parse(self, path: Path | str) -> str:
        file_path = Path(path)
        if not file_path.exists():
            raise DocumentParsingError(f"File not found: {file_path}")

        ext = file_path.suffix.lower()
        
        # Fast path for raw Markdown or plain text
        if ext in [".md", ".markdown", ".txt"]:
            try:
                content = file_path.read_text(encoding="utf-8")
                if content.strip():
                    return content
            except Exception as e:
                logger.warning(f"UTF-8 read failed for {file_path}, falling back to MarkItDown: {e}")

        try:
            logger.info(f"Converting document via MarkItDown: {file_path.name}")
            result = self.converter.convert(str(file_path))
            
            # Extract text/markdown content
            markdown_content = getattr(result, "text_content", None) or getattr(result, "markdown", None)
            if not markdown_content or not markdown_content.strip():
                raise DocumentParsingError(f"Document produced no text content: {file_path.name}")
            
            return markdown_content
        except Exception as e:
            logger.error(f"MarkItDown conversion error for {file_path}: {e}")
            raise DocumentParsingError(f"Failed to parse {file_path.name}: {str(e)}") from e
