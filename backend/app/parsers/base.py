from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseParser(ABC):
    """
    Abstract base class for all log parsers in ULPF.
    Every vendor adapter must implement `can_parse` and `parse`.
    """
    name: str = "BaseParser"
    vendor: str = "Generic"
    supported_formats: List[str] = ["generic"]
    version: str = "1.0.0"
    is_builtin: bool = True

    @abstractmethod
    def can_parse(self, raw_log: str) -> bool:
        """
        Determines if the raw log line matches this parser's signatures.
        Must return True only if confident of compatibility.
        """
        pass

    @abstractmethod
    def parse(self, raw_log: str) -> Dict[str, Any]:
        """
        Parses raw log string into structured intermediate dictionary.
        Returns extracted dictionary with standardized keys before normalization.
        """
        pass
