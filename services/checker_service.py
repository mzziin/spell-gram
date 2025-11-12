# services/checker_service.py
from core.spell_engine import SpellEngine
from core.grammer_engine import GrammarEngine

class CheckerService:
    def __init__(self):
        self.spell_engine = SpellEngine()
        self.grammar_engine = GrammarEngine()

    def check_text(self, text: str):
        """Runs spell + grammar checks"""
        spell_checked_text, spell_issues = self.spell_engine.correct(text)
        grammar_checked_text, grammar_issues = self.grammar_engine.correct(spell_checked_text)

        all_issues = spell_issues + grammar_issues
        return grammar_checked_text, all_issues
