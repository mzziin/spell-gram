# ui/result_view.py
import tkinter as tk
from typing import List
from core.models import Issue


class HighlightManager:
    """Manages error highlighting with non-conflicting tags."""

    # Tag names for different error types
    SPELLING_TAG = "error_spelling"
    GRAMMAR_TAG = "error_grammar"
    STYLE_TAG = "error_style"
    PUNCTUATION_TAG = "error_punctuation"
    OTHER_TAG = "error_other"

    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget
        self._configure_tags()

    def _configure_tags(self):
        """Configure all error highlight tags."""
        # Spelling: background highlight
        self.text_widget.tag_config(
            self.SPELLING_TAG,
            background="#FF6B6B",  # Red background
            foreground="white",
        )

        # Grammar: underline
        self.text_widget.tag_config(
            self.GRAMMAR_TAG, underline=True, underlinefg="#4ECDC4"  # Cyan underline
        )

        # Style: dashed underline (simulated with underline)
        self.text_widget.tag_config(
            self.STYLE_TAG, underline=True, underlinefg="#95E1D3"  # Light cyan
        )

        # Punctuation: dotted underline (simulated)
        self.text_widget.tag_config(
            self.PUNCTUATION_TAG, underline=True, underlinefg="#F38181"  # Light red
        )

        # Other grammar issues
        self.text_widget.tag_config(
            self.OTHER_TAG, underline=True, underlinefg="#AA96DA"  # Purple
        )

    def clear_all_highlights(self):
        """Remove all error highlights."""
        for tag in [
            self.SPELLING_TAG,
            self.GRAMMAR_TAG,
            self.STYLE_TAG,
            self.PUNCTUATION_TAG,
            self.OTHER_TAG,
        ]:
            self.text_widget.tag_remove(tag, "1.0", tk.END)

    def get_tag_for_issue(self, issue: Issue) -> str:
        """Determine which tag to use for an issue."""
        if issue.type == "spelling":
            return self.SPELLING_TAG
        elif issue.type == "grammar":
            return self.GRAMMAR_TAG
        elif issue.type == "style":
            return self.STYLE_TAG
        elif issue.type == "typographical":
            return self.PUNCTUATION_TAG
        else:
            return self.OTHER_TAG

    def highlight_issues(self, issues: List[Issue]):
        """
        Apply highlights to all issues.

        Uses different tags for different issue types to avoid conflicts.
        Background highlights (spelling) and underlines (grammar) can overlap safely.
        """
        # Clear existing highlights
        self.clear_all_highlights()

        if not issues:
            return

        # Apply highlights
        for issue in issues:
            tag = self.get_tag_for_issue(issue)

            # Convert character offsets to Tkinter indices
            start_idx = f"1.0+{issue.start}c"
            end_idx = f"1.0+{issue.end}c"

            # Apply tag
            self.text_widget.tag_add(tag, start_idx, end_idx)

    def get_issue_at_position(self, index: str, issues: List[Issue]) -> Issue:
        """Get the issue at a specific text position (for future tooltip support)."""
        # Convert Tkinter index to character offset
        offset = self.text_widget.count("1.0", index, "chars")[0]

        for issue in issues:
            if issue.start <= offset < issue.end:
                return issue

        return None


def highlight_errors(text_widget: tk.Text, issues: List[Issue]):
    """
    Main function to highlight errors (maintains backward compatibility).

    Args:
        text_widget: Tkinter Text widget
        issues: List of Issue objects to highlight
    """
    manager = HighlightManager(text_widget)
    manager.highlight_issues(issues)


def clear_highlights(text_widget: tk.Text):
    """Clear all error highlights from text widget."""
    manager = HighlightManager(text_widget)
    manager.clear_all_highlights()
