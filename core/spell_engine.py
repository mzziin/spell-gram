# core/spell_engine.py
import os
import re
from typing import List, Tuple
from symspellpy import SymSpell, Verbosity
from core.models import Issue

# Regex to extract words and punctuation
WORD_TOKEN_RE = re.compile(r"\b[\w']+\b|[^\w\s]", re.UNICODE)

# Protected words list (unchanged)
PROTECTED_WORDS = {
    "I",
    "i",
    "me",
    "you",
    "he",
    "she",
    "it",
    "we",
    "they",
    "him",
    "her",
    "them",
    "my",
    "your",
    "his",
    "her",
    "its",
    "our",
    "their",
    "mine",
    "yours",
    "hers",
    "ours",
    "theirs",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "do",
    "does",
    "did",
    "done",
    "a",
    "an",
    "the",
    "this",
    "that",
    "these",
    "those",
    "in",
    "on",
    "at",
    "by",
    "to",
    "of",
    "for",
    "with",
    "from",
    "after",
    "before",
    "over",
    "under",
    "between",
    "into",
    "during",
    "through",
    "without",
    "within",
    "and",
    "or",
    "but",
    "so",
    "nor",
    "yet",
    "can",
    "could",
    "will",
    "would",
    "shall",
    "should",
    "may",
    "might",
    "must",
    "very",
    "really",
    "just",
    "only",
    "still",
    "even",
    "ever",
    "never",
    "yes",
    "no",
    "not",
    "as",
    "up",
    "down",
    "out",
    "then",
    "than",
    "when",
    "while",
    "where",
    "what",
    "which",
    "who",
    "how",
    "why",
}


class SpellEngine:
    """SymSpell-based spell correction with context-aware ranking."""

    def __init__(self, grammar_validator=None):
        self.symspell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        self.grammar_validator = grammar_validator

        # Load dictionary
        base_path = os.path.dirname(os.path.abspath(__file__))
        dict_path = os.path.join(
            base_path, "..", "dictionaries", "symspell_frequency.txt"
        )
        dict_path = os.path.normpath(dict_path)

        if not os.path.exists(dict_path):
            raise FileNotFoundError(
                f"SymSpell dictionary not found:\n{dict_path}\n"
                "Download frequency_dictionary_en_82_765.txt and rename it."
            )

        if not self.symspell.load_dictionary(dict_path, term_index=0, count_index=1):
            raise RuntimeError("Failed to load SymSpell dictionary")

    def is_correct_word(self, word: str) -> bool:
        """Check if word is spelled correctly."""
        results = self.symspell.lookup(word, Verbosity.TOP, max_edit_distance=0)
        return bool(results and results[0].term.lower() == word.lower())

    def get_suggestions(self, word: str, max_suggestions: int = 5) -> List[str]:
        """Get top N spelling suggestions for a word."""
        suggestions = self.symspell.lookup(
            word, Verbosity.CLOSEST, max_edit_distance=2, include_unknown=False
        )
        return [s.term for s in suggestions[:max_suggestions]]

    def extract_context(
        self, text: str, start: int, end: int, context_words: int = 10
    ) -> Tuple[str, int, int]:
        """Extract sentence or context around the word."""
        # Try to find sentence boundaries
        before = text[:start]
        after = text[end:]

        # Look for sentence start (. ! ? or start of text)
        sent_start = max(
            before.rfind(".") + 1, before.rfind("!") + 1, before.rfind("?") + 1, 0
        )

        # Look for sentence end
        sent_end_period = after.find(".")
        sent_end_exclaim = after.find("!")
        sent_end_question = after.find("?")

        valid_ends = [
            e for e in [sent_end_period, sent_end_exclaim, sent_end_question] if e != -1
        ]
        sent_end = min(valid_ends) + 1 if valid_ends else len(after)
        sent_end = end + sent_end

        context = text[sent_start:sent_end].strip()
        word_start_in_context = start - sent_start
        word_end_in_context = end - sent_start

        return context, word_start_in_context, word_end_in_context

    def rank_suggestion_with_grammar(
        self, original_text: str, word_start: int, word_end: int, suggestions: List[str]
    ) -> str:
        """Rank suggestions by grammar errors they produce."""
        if not self.grammar_validator or not suggestions:
            return suggestions[0] if suggestions else ""

        # Extract context
        context, ctx_start, ctx_end = self.extract_context(
            original_text, word_start, word_end
        )

        original_word = original_text[word_start:word_end]

        best_suggestion = suggestions[0]
        min_error_score = float("inf")

        for suggestion in suggestions[:3]:  # Test top 3 suggestions
            # Replace word in context
            modified_context = context[:ctx_start] + suggestion + context[ctx_end:]

            # Check grammar
            error_score = self.grammar_validator.score_text(modified_context)

            if error_score < min_error_score:
                min_error_score = error_score
                best_suggestion = suggestion

        return best_suggestion

    def detect_errors(self, text: str) -> List[Issue]:
        """Detect spelling errors and return as Issue objects."""
        issues = []
        tokens = list(WORD_TOKEN_RE.finditer(text))

        for tok in tokens:
            word = tok.group()

            # Skip punctuation, numbers
            if not re.match(r"^[\w']+$", word) or any(ch.isdigit() for ch in word):
                continue

            # Protected words
            if word.lower() in PROTECTED_WORDS:
                if self.is_correct_word(word) or self.is_correct_word(word.lower()):
                    continue

            # Check spelling
            if not self.is_correct_word(word):
                suggestions = self.get_suggestions(word)

                if suggestions:
                    # Rank with grammar if available
                    best = (
                        self.rank_suggestion_with_grammar(
                            text, tok.start(), tok.end(), suggestions
                        )
                        if self.grammar_validator
                        else suggestions[0]
                    )

                    issues.append(
                        Issue(
                            type="spelling",
                            start=tok.start(),
                            end=tok.end(),
                            original=word,
                            suggestion=best,
                            suggestions=suggestions,
                            message=f"Possible spelling error: '{word}'",
                        )
                    )

        return issues

    def correct(self, text: str) -> Tuple[str, List[Issue]]:
        """Detect errors but don't auto-correct (for Check operation)."""
        issues = self.detect_errors(text)
        return text, issues
