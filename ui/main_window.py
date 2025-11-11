# ui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.checker_service import CheckerService

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Spell Checker Pro")
        self.root.geometry("900x600")

        self.service = CheckerService()

        self.create_widgets()

    def create_widgets(self):
        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, pady=5)

        check_btn = ttk.Button(toolbar, text="Check Text", command=self.check_text)
        check_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(toolbar, text="Clear", command=self.clear_text)
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Text area
        self.text_area = tk.Text(self.root, wrap=tk.WORD, font=("Consolas", 13))
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Status bar
        self.status_label = ttk.Label(self.root, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def check_text(self):
        text = self.text_area.get("1.0", tk.END)
        if not text.strip():
            messagebox.showinfo("Info", "Please enter some text to check.")
            return

        corrected_text, issues = self.service.check_text(text)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, corrected_text)

        self.status_label.config(text=f"Found {len(issues)} issue(s) corrected.")

    def clear_text(self):
        self.text_area.delete("1.0", tk.END)
        self.status_label.config(text="Cleared")

    def run(self):
        self.root.mainloop()
