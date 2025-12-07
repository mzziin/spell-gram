# core/grammar_engine.py
import language_tool_python
from core.models import Issue

class GrammarEngine:
    
    def __init__(self):
        # Initialize LanguageTool for English
        self.tool = language_tool_python.LanguageTool('en-US')
        
        # Categories to skip (pure spelling checks, not grammar-related)
        self.skip_categories = {
            'TYPOS',  # Pure typos
            'MISSPELLING',  # Dictionary spelling errors
        }
        
        # Rule IDs to skip (pure spelling, not grammar)
        self.skip_rule_ids = {
            'MORFOLOGIK_RULE_EN_US',  # Pure spelling dictionary
            'HUNSPELL_RULE',  # Another spelling rule
            'HUNSPELL_NO_SUGGEST_RULE',
        }
        
    def check(self, text: str):
        """
        Check text for grammar errors.
        Includes grammar-related word choice (tense, agreement) but skips pure spelling.
        Returns list of grammar issues.
        """
        # Get all matches from LanguageTool
        matches = self.tool.check(text)
        
        issues = []
        for match in matches:
            # Skip pure spelling/typo errors
            if self._is_pure_spelling_error(match):
                continue
                
            # Get the error range
            start = match.offset
            end = match.offset + match.error_length
            original_text = text[start:end]
            
            # Get suggestions (limit to 3)
            suggestions = match.replacements[:3] if match.replacements else []
            
            # Create grammar issue
            issue = Issue(
                type="grammar",
                start=start,
                end=end,
                original=original_text,
                suggestion=suggestions[0] if suggestions else "",
                suggestions=suggestions,
                message=match.message
            )
            issues.append(issue)
        
        return issues
    
    def _is_pure_spelling_error(self, match):
        """
        Determine if a match is purely a spelling error (skip it)
        vs a grammar error that involves word choice (keep it).
        """
        rule_id = match.rule_id
        category = match.category if hasattr(match, 'category') else ''
        
        # Skip if it's in pure spelling categories
        if category in self.skip_categories:
            return True
        
        # Skip if it's a pure spelling rule ID
        for skip_id in self.skip_rule_ids:
            if skip_id in rule_id:
                return True
        
        return False
    
    def correct(self, text: str, issues: list[Issue]):
        # Sort issues by position (reverse order)
        sorted_issues = sorted(issues, key=lambda x: x.start, reverse=True)
        
        corrected_text = text
        for issue in sorted_issues:
            if issue.suggestion:
                # Replace the error with the suggestion
                corrected_text = (
                    corrected_text[:issue.start] + 
                    issue.suggestion + 
                    corrected_text[issue.end:]
                )
        
        return corrected_text
    
    def __del__(self):
        """Cleanup LanguageTool resources."""
        if hasattr(self, 'tool'):
            self.tool.close()