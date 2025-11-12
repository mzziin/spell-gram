# ui/results_view.py
import tkinter as tk
from core.models import Issue

def highlight_errors(text_widget, issues: list[Issue]):
    """Highlight all error ranges in red underline."""
    text_widget.tag_remove("error", "1.0", tk.END)
    text_widget.tag_config("error", foreground="red", underline=1)

    for issue in issues:
        start_idx = f"1.0+{issue.start}c"
        end_idx = f"1.0+{issue.end}c"
        text_widget.tag_add("error", start_idx, end_idx)
