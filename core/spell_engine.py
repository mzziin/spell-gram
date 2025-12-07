# core/spell_engine.py
import os
import re
from symspellpy import SymSpell, Verbosity
from core.models import Issue

# Regex to extract words and punctuation
WORD_TOKEN_RE = re.compile(r"\b[\w']+\b|[^\w\s]", re.UNICODE)

# Protected English words (case-insensitive)
PROTECTED_WORDS = {
    "I", "i", "me", "you", "he", "she", "it", "we", "they",
    "him", "her", "them", "my", "your", "his", "her", "its", 
    "our", "their", "mine", "yours", "hers", "ours", "theirs",
    "am", "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "done", "a", "an", "the", "this", 
    "that", "these", "those", "in", "on", "at", "by", "to", 
    "of", "for", "with", "from", "after", "before", "over", 
    "under", "between", "into", "during", "through", "without",
    "within", "and", "or", "but", "so", "nor", "yet", "can",
    "could", "will", "would", "shall", "should", "may", "might",
    "must", "very", "really", "just", "only", "still", "even",
    "ever", "never", "yes", "no", "not", "as", "up", "down",
    "out", "then", "than", "when", "while", "where", "what",
    "which", "who", "how", "why"
}


class SpellEngine:

    def __init__(self):
        self.symspell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        dict_path = os.path.join(base_path, "..", "dictionaries", "symspell_frequency.txt")
        dict_path = os.path.normpath(dict_path)

        if not os.path.exists(dict_path):
            raise FileNotFoundError(
                f"SymSpell dictionary not found:\n{dict_path}\n"
            )

        if not self.symspell.load_dictionary(dict_path, term_index=0, count_index=1):
            raise RuntimeError("Failed to load SymSpell dictionary")

    def is_correct_word(self, word: str) -> bool:
        results = self.symspell.lookup(word, Verbosity.TOP, max_edit_distance=0)
        return bool(results and results[0].term.lower() == word.lower())

    def check(self, text: str):
        """
        Check text for spelling errors.
        Returns list of spelling issues with up to 3 suggestions each.
        """
        issues = []
        tokens = list(WORD_TOKEN_RE.finditer(text))

        for tok in tokens:
            word = tok.group()

            # Skip punctuation/symbols
            if not re.match(r"^[\w']+$", word):
                continue

            # Skip numbers
            if any(ch.isdigit() for ch in word):
                continue

            # Check protected words
            if word.lower() in PROTECTED_WORDS:
                if self.is_correct_word(word) or self.is_correct_word(word.lower()):
                    continue

            # Check if word is correct
            if self.is_correct_word(word):
                continue

            # Get suggestions for misspelled word
            suggestions = self.symspell.lookup(
                word,
                Verbosity.ALL,
                max_edit_distance=2,
                include_unknown=False
            )

            if suggestions:
                # Get top suggestions, prioritizing those with edit distance <= 2
                top_suggestions = []
                
                for s in suggestions:
                    if len(top_suggestions) >= 5:
                        break
                    top_suggestions.append(s.term)
                
                # Remove duplicates while preserving order
                seen = set()
                unique_suggestions = []
                for s in top_suggestions:
                    s_lower = s.lower()
                    if s_lower not in seen and s_lower != word.lower():
                        seen.add(s_lower)
                        unique_suggestions.append(s)
                
                # Limit to top 3
                final_suggestions = unique_suggestions[:3]
                
                # Only create issue if we have valid suggestions
                if final_suggestions:
                    issues.append(
                        Issue(
                            type="spelling",
                            start=tok.start(),
                            end=tok.end(),
                            original=word,
                            suggestion=final_suggestions[0],
                            suggestions=final_suggestions
                        )
                    )

        return issues
    
    def apply_correction(self, text: str, issue: Issue, chosen_word: str):
        """
        Apply a single correction to text.
        Returns the corrected text.
        """
        return text[:issue.start] + chosen_word + text[issue.end:]