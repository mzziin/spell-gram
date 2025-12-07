# core/grammar_engine.py
import language_tool_python
from core.models import Issue

class GrammarEngine:
    """Grammar checking engine using LanguageTool."""
    
    def __init__(self):
        # Initialize LanguageTool for English
        self.tool = language_tool_python.LanguageTool('en-US')
        
    def check(self, text: str):
        """
        Check text for grammar errors only (no spelling).
        Returns list of grammar issues.
        """
        # Get all matches from LanguageTool
        matches = self.tool.check(text)
        
        issues = []
        for match in matches:
            # Skip spelling errors (we handle those separately)
            if 'MORFOLOGIK_RULE' in match.rule_id or 'SPELLING_RULE' in match.rule_id:
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
    
    def correct(self, text: str, issues: list[Issue]):
        """
        Apply corrections to text based on issues.
        Processes from end to start to maintain correct positions.
        """
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