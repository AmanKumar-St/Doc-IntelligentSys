class DocumentIntelligenceException(Exception):
    """Base exception for Document Intelligence system."""
    pass


class DocumentParsingError(DocumentIntelligenceException):
    """Raised when document extraction fails."""
    pass


class ChunkingError(DocumentIntelligenceException):
    """Raised when chunking fails."""
    pass


class VectorStorageError(DocumentIntelligenceException):
    """Raised when vector database operations fail."""
    pass


class ProviderError(DocumentIntelligenceException):
    """Raised when an external model provider fails."""
    pass


class CitationValidationError(DocumentIntelligenceException):
    """Raised when model response contains hallucinated or invalid citations."""
    pass
