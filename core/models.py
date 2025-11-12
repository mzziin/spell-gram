# core/models.py
from dataclasses import dataclass
from typing import List

@dataclass
class Issue:
    """Represents a spelling or grammar issue."""
    type: str                # "spelling" or "grammar"
    start: int               # character start index
    end: int                 # character end index
    original: str = ""       # original text (for spelling)
    suggestion: str = ""     # top suggestion (for spelling)
    suggestions: List[str] = None  # all possible suggestions (for grammar)
    message: str = ""        # grammar rule message

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
