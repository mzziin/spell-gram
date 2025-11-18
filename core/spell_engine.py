# core/spell_engine.py
import os
import re
from symspellpy import SymSpell, Verbosity
from core.models import Issue

# Regex to extract words and punctuation
WORD_TOKEN_RE = re.compile(r"\b[\w']+\b|[^\w\s]", re.UNICODE)

# Full list of protected English words (case-insensitive)
PROTECTED_WORDS = {
    # Pronouns
    "I", "i", "me", "you", "he", "she", "it", "we", "they",
    "him", "her", "them",

    # Possessive pronouns
    "my", "your", "his", "her", "its", "our", "their",
    "mine", "yours", "hers", "ours", "theirs",

    # Auxiliary verbs
    "am", "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "done",

    # Articles & determiners
    "a", "an", "the", "this", "that", "these", "those",

    # Prepositions
    "in", "on", "at", "by", "to", "of", "for", "with",
    "from", "after", "before", "over", "under", "between",
    "into", "during", "through", "without", "within",

    # Conjunctions
    "and", "or", "but", "so", "nor", "yet",

    # Modal verbs
    "can", "could", "will", "would", "shall", "should",
    "may", "might", "must",

    # Common adverbs
    "very", "really", "just", "only", "still", "even",
    "ever", "never",

    # Common words
    "yes", "no", "not", "as", "up", "down", "out",
    "then", "than", "when", "while", "where", "what",
    "which", "who", "how", "why"
}


class SpellEngine:
    """SymSpell-based spell correction engine with smart-protection logic."""

    def __init__(self):
        # Initialize SymSpell
        self.symspell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

        # Path to SymSpell dictionary
        base_path = os.path.dirname(os.path.abspath(__file__))
        dict_path = os.path.join(base_path, "..", "dictionaries", "symspell_frequency.txt")
        dict_path = os.path.normpath(dict_path)

        if not os.path.exists(dict_path):
            raise FileNotFoundError(
                f"SymSpell dictionary not found:\n{dict_path}\n"
                "Download frequency_dictionary_en_82_765.txt and rename it to symspell_frequency.txt"
            )

        if not self.symspell.load_dictionary(dict_path, term_index=0, count_index=1):
            raise RuntimeError("Failed to load SymSpell dictionary")

    # ------------------------------------------------------------------
    def is_correct_word(self, word: str) -> bool:
        """Check if a word is spelled correctly (exact match only)."""
        results = self.symspell.lookup(word, Verbosity.TOP, max_edit_distance=0)
        return bool(results and results[0].term.lower() == word.lower())

    # ------------------------------------------------------------------
    def correct(self, text: str):
        """Return corrected text + list of spelling issues."""
        issues = []
        corrected_tokens = []

        tokens = list(WORD_TOKEN_RE.finditer(text))

        for tok in tokens:
            word = tok.group()

            # Skip punctuation/symbols
            if not re.match(r"^[\w']+$", word):
                corrected_tokens.append(word)
                continue

            # Skip numbers
            if any(ch.isdigit() for ch in word):
                corrected_tokens.append(word)
                continue

            # Protected Words (case-insensitive)
            if word.lower() in PROTECTED_WORDS:
                # If spelled correctly → keep it unchanged
                if self.is_correct_word(word) or self.is_correct_word(word.lower()):
                    corrected_tokens.append(word)
                    continue
                # If misspelled → allow SymSpell to fix it normally

            # SymSpell correction
            suggestions = self.symspell.lookup(
                word,
                Verbosity.TOP,
                max_edit_distance=2
            )

            if suggestions:
                best = suggestions[0].term

                # Register issue if changed
                if best.lower() != word.lower():
                    issues.append(
                        Issue(
                            type="spelling",
                            start=tok.start(),
                            end=tok.end(),
                            original=word,
                            suggestion=best,
                            suggestions=[s.term for s in suggestions]
                        )
                    )

                corrected_tokens.append(best)
            else:
                corrected_tokens.append(word)

        corrected_text = self._rebuild_text(text, tokens, corrected_tokens)
        return corrected_text, issues

    # ------------------------------------------------------------------
    def _rebuild_text(self, original_text, tokens, corrected_tokens):
        """Rebuild the final corrected text while preserving original spacing."""
        result = []
        last = 0

        for tok, new in zip(tokens, corrected_tokens):
            result.append(original_text[last:tok.start()])
            result.append(new)
            last = tok.end()

        result.append(original_text[last:])
        return "".join(result)
