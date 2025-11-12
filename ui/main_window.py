# ui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.checker_service import CheckerService
from ui.result_view import highlight_errors
from core.models import Issue

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Offline Spell Checker")
        self.root.geometry("900x600")

        self.service = CheckerService()
        self.issues: list[Issue] = []

        self.create_widgets()

    def create_widgets(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, pady=5)

        check_btn = ttk.Button(toolbar, text="Check", command=self.check_text)
        check_btn.pack(side=tk.LEFT, padx=5)

        fix_btn = ttk.Button(toolbar, text="Fix", command=self.fix_text)
        fix_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(toolbar, text="Clear", command=self.clear_text)
        clear_btn.pack(side=tk.LEFT, padx=5)

        self.text_area = tk.Text(self.root, wrap=tk.WORD, font=("Consolas", 13))
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        self.status_label = ttk.Label(self.root, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def check_text(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Info", "Please enter some text to check.")
            return

        corrected_text, self.issues = self.service.check_text(text)
        if not self.issues:
            self.status_label.config(text="No errors found ✅")
            messagebox.showinfo("Check Complete", "No errors found.")
            return

        highlight_errors(self.text_area, self.issues)
        self.status_label.config(text=f"{len(self.issues)} issue(s) found ⚠️")

    def fix_text(self):
        if not self.issues:
            messagebox.showinfo("Info", "No issues to fix.")
            return

        text = self.text_area.get("1.0", tk.END)
        # Apply corrections (reverse order to avoid offset shifts)
        for issue in reversed(self.issues):
            if issue.suggestion:
                text = text[:issue.start] + issue.suggestion + text[issue.end:]
            elif issue.suggestions:
                text = text[:issue.start] + issue.suggestions[0] + text[issue.end:]

        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, text)
        self.text_area.tag_remove("error", "1.0", tk.END)
        self.status_label.config(text="All issues fixed ✅")
        self.issues.clear()

    def clear_text(self):
        self.text_area.delete("1.0", tk.END)
        self.text_area.tag_remove("error", "1.0", tk.END)
        self.issues.clear()
        self.status_label.config(text="Cleared")

    def run(self):
        self.root.mainloop()
