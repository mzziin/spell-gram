# services/checker_service.py
from core.spell_engine import SpellEngine
from core.grammer_engine import GrammarEngine
from core.models import Issue

class CheckerService:
    """Handles orchestration between spell and grammar checks."""

    def __init__(self):
        self.spell_engine = SpellEngine()
        self.grammar_engine = GrammarEngine()

    def check_text(self, text: str):
        """Runs both checks and returns final text + all issues."""
        spell_checked_text, spell_issues = self.spell_engine.correct(text)
        grammar_checked_text, grammar_issues = self.grammar_engine.correct(spell_checked_text)

        all_issues = spell_issues + grammar_issues
        all_issues.sort(key=lambda i: i.start)  # sort by text order

        return grammar_checked_text, all_issues
