# core/grammar_engine.py
import language_tool_python

class GrammarEngine:
    def __init__(self):
        self.tool = language_tool_python.LanguageTool('en-US')

    def correct(self, text: str):
        matches = self.tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)

        issues = []
        for m in matches:
            issues.append({
                "type": "grammar",
                "message": m.message,
                "suggestions": m.replacements,
                "start": m.offset,
                "end": m.offset + m.errorLength
            })

        return corrected_text, issues
