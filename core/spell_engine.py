# core/spell_engine.py
from textblob import TextBlob

class SpellEngine:
    def correct(self, text: str):
        blob = TextBlob(text)
        corrected_text = str(blob.correct())

        issues = []
        words = text.split()
        corrected_words = corrected_text.split()

        for i, word in enumerate(words):
            if i < len(corrected_words) and word != corrected_words[i]:
                issues.append({
                    "type": "spelling",
                    "original": word,
                    "suggestion": corrected_words[i],
                    "start": text.find(word),
                    "end": text.find(word) + len(word)
                })

        return corrected_text, issues
