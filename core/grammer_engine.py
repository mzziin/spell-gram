# core/grammar_engine.py
import language_tool_python
from typing import List, Tuple
from core.models import Issue


class GrammarEngine:
    """LanguageTool-based grammar checker with spelling disabled."""

    def __init__(self):
        self.tool = None
        self._initialize_tool()

    def _initialize_tool(self):
        """Initialize LanguageTool with spelling rules disabled."""
        try:
            self.tool = language_tool_python.LanguageTool("en-US")

            # Disable all spelling-related rules
            spelling_rules = [
                "MORFOLOGIK_RULE_EN_US",  # Main spelling rule
                "MORFOLOGIK_RULE_EN",
                "HUNSPELL_RULE",
                "HUNSPELL_NO_SUGGEST_RULE",
                "SPELLING_RULE",
            ]

            self.tool.disabled_rules = spelling_rules

        except Exception as e:
            print(f"Warning: Failed to initialize LanguageTool: {e}")
            self.tool = None

    def restart_tool(self):
        """Restart LanguageTool if it crashes."""
        try:
            if self.tool:
                self.tool.close()
        except:
            pass
        self._initialize_tool()

    def score_text(self, text: str) -> float:
        """Score text by grammar errors (for ranking spelling suggestions)."""
        if not self.tool:
            return 0.0

        try:
            matches = self.tool.check(text)

            # Calculate weighted error score
            score = 0.0
            for match in matches:
                # Ignore spelling-related matches
                rule_id = match.ruleId
                if "SPELL" in rule_id or "MORFOLOGIK" in rule_id:
                    continue

                # Weight by issue type
                if match.ruleIssueType == "grammar":
                    score += 3.0
                elif match.ruleIssueType == "typographical":
                    score += 2.0
                elif match.ruleIssueType == "style":
                    score += 1.0
                else:
                    score += 1.5

            return score

        except Exception as e:
            print(f"Error scoring text: {e}")
            return 0.0

    def detect_errors(self, text: str) -> List[Issue]:
        """Detect grammar, style, and punctuation errors."""
        if not self.tool:
            return []

        issues = []

        try:
            matches = self.tool.check(text)

            for match in matches:
                # Skip spelling rules
                rule_id = match.ruleId
                if "SPELL" in rule_id or "MORFOLOGIK" in rule_id:
                    continue

                # Determine issue subtype
                issue_type = match.ruleIssueType or "grammar"

                # Get suggestions
                suggestions = match.replacements[:5] if match.replacements else []
                best_suggestion = suggestions[0] if suggestions else ""

                issues.append(
                    Issue(
                        type=issue_type,  # 'grammar', 'style', 'typographical', etc.
                        start=match.offset,
                        end=match.offset + match.errorLength,
                        original=text[match.offset : match.offset + match.errorLength],
                        suggestion=best_suggestion,
                        suggestions=suggestions,
                        message=match.message,
                    )
                )

        except Exception as e:
            print(f"Error checking grammar: {e}")
            self.restart_tool()

        return issues

    def correct(self, text: str) -> Tuple[str, List[Issue]]:
        """Detect errors but don't auto-correct (for Check operation)."""
        issues = self.detect_errors(text)
        return text, issues

    def close(self):
        """Clean up LanguageTool resources."""
        if self.tool:
            try:
                self.tool.close()
            except:
                pass
