# core/grammar_engine.py
import re

class GrammarEngine:
    def correct(self, text: str):
        """Very simple offline grammar checks (rule-based)."""
        issues = []
        corrected_text = text

        # Rule 1: Double spaces
        if "  " in text:
            corrected_text = corrected_text.replace("  ", " ")
            issues.append({
                "type": "grammar",
                "message": "Removed extra spaces.",
                "suggestions": [],
                "start": text.find("  "),
                "end": text.find("  ") + 2
            })

        # Rule 2: Sentence capitalization
        sentences = re.split(r'(?<=[.!?]) +', corrected_text)
        corrected_sentences = []
        for s in sentences:
            if s and not s[0].isupper():
                issues.append({
                    "type": "grammar",
                    "message": "Sentence should start with a capital letter.",
                    "suggestions": [s.capitalize()],
                    "start": corrected_text.find(s),
                    "end": corrected_text.find(s) + len(s)
                })
                corrected_sentences.append(s.capitalize())
            else:
                corrected_sentences.append(s)
        corrected_text = " ".join(corrected_sentences)

        return corrected_text, issues
