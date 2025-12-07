# services/checker_service.py
import threading
from typing import List, Tuple, Callable
from core.spell_engine import SpellEngine
from core.grammer_engine import GrammarEngine
from core.models import Issue


class CheckerService:
    """Orchestrates spell and grammar checking with threading support."""

    def __init__(self):
        self.grammar_engine = GrammarEngine()
        self.spell_engine = SpellEngine(grammar_validator=self.grammar_engine)
        self._check_thread = None
        self._fix_thread = None

    def check_text(self, text: str, callback: Callable = None):
        """
        Run spell + grammar checks in background thread.

        Args:
            text: Text to check
            callback: Function to call with (issues, error) when complete
        """
        if callback:
            self._check_thread = threading.Thread(
                target=self._check_async, args=(text, callback), daemon=True
            )
            self._check_thread.start()
        else:
            # Synchronous mode
            return self._check_sync(text)

    def _check_sync(self, text: str) -> Tuple[List[Issue], str]:
        """Synchronous check (returns issues and error message)."""
        try:
            all_issues = []

            # 1. Spell check
            _, spell_issues = self.spell_engine.correct(text)
            all_issues.extend(spell_issues)

            # 2. Grammar check (spelling disabled in LT)
            _, grammar_issues = self.grammar_engine.correct(text)
            all_issues.extend(grammar_issues)

            # Sort by position
            all_issues.sort(key=lambda i: i.start)

            return all_issues, None

        except Exception as e:
            return [], str(e)

    def _check_async(self, text: str, callback: Callable):
        """Async check wrapper."""
        issues, error = self._check_sync(text)
        callback(issues, error)

    def fix_text(self, text: str, issues: List[Issue], callback: Callable = None):
        """
        Apply all corrections to text.

        Args:
            text: Original text
            issues: List of issues to fix
            callback: Function to call with (corrected_text, error) when complete
        """
        if callback:
            self._fix_thread = threading.Thread(
                target=self._fix_async, args=(text, issues, callback), daemon=True
            )
            self._fix_thread.start()
        else:
            # Synchronous mode
            return self._fix_sync(text, issues)

    def _fix_sync(self, text: str, issues: List[Issue]) -> Tuple[str, str]:
        """
        Apply all corrections in reverse order to maintain indices.

        Returns:
            (corrected_text, error_message)
        """
        try:
            if not issues:
                return text, None

            # Sort issues by position (reverse order for safe replacement)
            sorted_issues = sorted(issues, key=lambda i: i.start, reverse=True)

            corrected = text

            for issue in sorted_issues:
                if issue.suggestion:
                    # Replace error with suggestion
                    corrected = (
                        corrected[: issue.start]
                        + issue.suggestion
                        + corrected[issue.end :]
                    )

            return corrected, None

        except Exception as e:
            return text, str(e)

    def _fix_async(self, text: str, issues: List[Issue], callback: Callable):
        """Async fix wrapper."""
        corrected, error = self._fix_sync(text, issues)
        callback(corrected, error)

    def verify_fixes(self, text: str) -> Tuple[List[Issue], str]:
        """
        Optional: Re-run checks after fixing to verify.

        Returns:
            (remaining_issues, error_message)
        """
        return self._check_sync(text)

    def close(self):
        """Clean up resources."""
        self.grammar_engine.close()
