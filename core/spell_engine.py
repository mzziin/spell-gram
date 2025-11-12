# core/spell_engine.py
from textblob import TextBlob
from core.models import Issue

class SpellEngine:
    """Handles spelling correction using TextBlob."""

    def correct(self, text: str):
        blob = TextBlob(text)
        corrected_text = str(blob.correct())

        issues = []
        words = text.split()
        corrected_words = corrected_text.split()

        offset = 0  # track text index positions

        for i, word in enumerate(words):
            pos = text.find(word, offset)
            offset = pos + len(word)
            if i < len(corrected_words) and word != corrected_words[i]:
                issues.append(
                    Issue(
                        type="spelling",
                        start=pos,
                        end=pos + len(word),
                        original=word,
                        suggestion=corrected_words[i]
                    )
                )
        return corrected_text, issues
