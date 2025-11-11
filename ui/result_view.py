# ui/results_view.py
# For later enhancement: highlights incorrect words in red

import tkinter as tk

def highlight_errors(text_widget, errors):
    """Highlight misspelled words in red"""
    text_widget.tag_remove("error", "1.0", tk.END)
    text_widget.tag_config("error", foreground="red", underline=1)

    for err in errors:
        start = f"1.0+{err['start']}c"
        end = f"1.0+{err['end']}c"
        text_widget.tag_add("error", start, end)
