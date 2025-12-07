# services/checker_service.py
from core.spell_engine import SpellEngine
from core.grammer_engine import GrammarEngine
from core.models import Issue

class CheckerService:

    def __init__(self):
        self.spell_engine = SpellEngine()
        self.grammar_engine = GrammarEngine()

    def check_spelling(self, text: str):
        """
        Check text for spelling errors only.
        Returns list of spelling issues.
        """
        return self.spell_engine.check(text)
    
    def apply_spell_correction(self, text: str, issue: Issue, chosen_word: str):
        """
        Apply a single spelling correction.
        Returns corrected text.
        """
        return self.spell_engine.apply_correction(text, issue, chosen_word)
    
    def check_grammar(self, text: str):
        """
        Check text for grammar errors only.
        Returns list of grammar issues.
        """
        return self.grammar_engine.check(text)
    
    def fix_grammar(self, text: str, issues: list[Issue]):
        """
        Apply all grammar corrections at once.
        Returns corrected text.
        """
        return self.grammar_engine.correct(text, issues)