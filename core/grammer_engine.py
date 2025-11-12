# core/grammar_engine.py
import re
from core.models import Issue

class GrammarEngine:

    def correct(self, text: str):
        issues = []
        corrected_text = text

        # Rule 1: Double spaces
        for match in re.finditer(r' {2,}', text):
            start, end = match.span()
            issues.append(
                Issue(
                    type="grammar",
                    start=start,
                    end=end,
                    message="Multiple consecutive spaces.",
                    suggestions=[" "]
                )
            )
            corrected_text = corrected_text.replace("  ", " ")

        # Rule 2: Sentence capitalization
        sentences = re.split(r'(?<=[.!?]) +', corrected_text)
        new_sentences = []
        position = 0
        for s in sentences:
            if s and not s[0].isupper():
                start = corrected_text.find(s, position)
                end = start + len(s)
                issues.append(
                    Issue(
                        type="grammar",
                        start=start,
                        end=end,
                        message="Sentence should start with a capital letter.",
                        suggestions=[s.capitalize()]
                    )
                )
                new_sentences.append(s.capitalize())
            else:
                new_sentences.append(s)
            position += len(s) + 1
        corrected_text = " ".join(new_sentences)

        return corrected_text, issues
