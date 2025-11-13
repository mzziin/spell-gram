import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from services.checker_service import CheckerService
from ui.result_view import highlight_errors
from core.models import Issue


class MainWindow:
    def __init__(self):
        # Create themed window with dark theme
        self.root = tb.Window(themename="darkly")
        self.root.title("Spell Checker")
        self.root.geometry("1200x800")

        # Make the window responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.service = CheckerService()
        self.issues: list[Issue] = []

        self.create_widgets()

    def create_widgets(self):
        # --- Main container with gradient effect ---
        main_frame = tb.Frame(self.root, bootstyle="dark")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.configure(style="Dark.TFrame")

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)  # header
        main_frame.rowconfigure(1, weight=0)  # subtitle
        main_frame.rowconfigure(2, weight=1)  # text area
        main_frame.rowconfigure(3, weight=0)  # buttons
        main_frame.rowconfigure(4, weight=0)  # status

        # --- Header Section ---
        header_frame = tb.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(60, 10))
        header_frame.columnconfigure(0, weight=1)

        # Icon + Title
        title_container = tb.Frame(header_frame, bootstyle="dark")
        title_container.grid(row=0, column=0)
    
        title_label = tb.Label(
            title_container,
            text="Spell Checker",
            font=("Segoe UI", 52, "bold"),
        )
        title_label.pack(side="left")

    
        # --- Text Area Container with modern styling ---
        text_container = tb.Frame(main_frame, bootstyle="dark")
        text_container.grid(row=2, column=0, sticky="nsew", padx=120, pady=(0, 40))
        text_container.columnconfigure(0, weight=1)
        text_container.rowconfigure(0, weight=1)

        # Inner frame for border effect
        text_frame = tb.Frame(text_container, bootstyle="dark")
        text_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.text_area = tb.Text(
            text_frame,
            wrap="word",
            font=("Segoe UI", 13),
            background="#1A1A1A",
            foreground="#E5E5E5",
            insertbackground="#FF8C42",
            borderwidth=0,
            relief="flat",
            highlightthickness=2,
            highlightbackground="#2A2A2A",
            highlightcolor="#FF8C42"
        )
        self.text_area.grid(row=0, column=0, sticky="nsew")

        # Placeholder text
        placeholder = "Type or paste your text here..."
        self.text_area.insert("1.0", placeholder)
        self.text_area.config(foreground="#4A5568")

        def on_focus_in(event):
            if self.text_area.get("1.0", "end-1c") == placeholder:
                self.text_area.delete("1.0", "end")
                self.text_area.config(foreground="#E5E5E5")

        def on_focus_out(event):
            if not self.text_area.get("1.0", "end-1c").strip():
                self.text_area.insert("1.0", placeholder)
                self.text_area.config(foreground="#4A5568")

        self.text_area.bind("<FocusIn>", on_focus_in)
        self.text_area.bind("<FocusOut>", on_focus_out)

        # --- Scrollbar (minimal design) ---
        scrollbar = tb.Scrollbar(text_frame, command=self.text_area.yview, bootstyle="rounded")
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(5, 5))
        self.text_area.config(yscrollcommand=scrollbar.set)

        # --- Modern Button Panel ---
        button_container = tb.Frame(main_frame)
        button_container.grid(row=3, column=0, pady=(0, 40))

        # Custom styled buttons with hover effect
        check_btn = tb.Button(
            button_container,
            text="🔍 Check Text",
            bootstyle="warning-outline",
            width=18,
            command=self.check_text,
        )
        check_btn.grid(row=0, column=0, padx=12)
        check_btn.configure(
            cursor="hand2"
        )

        fix_btn = tb.Button(
            button_container,
            text="✓ Fix Errors",
            bootstyle="success-outline",
            width=18,
            command=self.fix_text,
        )
        fix_btn.grid(row=0, column=1, padx=12)
        fix_btn.configure(cursor="hand2")

        clear_btn = tb.Button(
            button_container,
            text="⟲ Clear",
            bootstyle="outline",
            width=18,
            command=self.clear_text,
        )
        clear_btn.grid(row=0, column=2, padx=12)
        clear_btn.configure(cursor="hand2")

        # --- Status Bar (modern minimal design) ---
        status_container = tb.Frame(main_frame, bootstyle="dark")
        status_container.grid(row=4, column=0, sticky="ew", pady=(0, 30))
        status_container.columnconfigure(0, weight=1)

    # ---------------- Logic ----------------
    def check_text(self):
        text = self.text_area.get("1.0", "end").strip()
        placeholder = "Type or paste your text here..."
        
        if not text or text == placeholder:
            messagebox.showinfo("Info", "Please enter some text to check.")
            return

        corrected_text, self.issues = self.service.check_text(text)
        if not self.issues:
            self.status_label.config(
                text="✨ Perfect! No errors found",
                foreground="#10B981"
            )
            messagebox.showinfo("Check Complete", "No errors found.")
            return

        highlight_errors(self.text_area, self.issues)
        self.status_label.config(
            text=f"⚠️ Found {len(self.issues)} issue{'s' if len(self.issues) > 1 else ''}",
            foreground="#F59E0B"
        )

    def fix_text(self):
        if not self.issues:
            messagebox.showinfo("Info", "No issues to fix.")
            return

        text = self.text_area.get("1.0", "end")
        for issue in reversed(self.issues):
            if issue.suggestion:
                text = text[:issue.start] + issue.suggestion + text[issue.end:]
            elif issue.suggestions:
                text = text[:issue.start] + issue.suggestions[0] + text[issue.end:]

        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", text)
        self.text_area.tag_remove("error", "1.0", "end")
        self.status_label.config(
            text="✓ All issues fixed successfully",
            foreground="#10B981"
        )
        self.issues.clear()

    def clear_text(self):
        self.text_area.delete("1.0", "end")
        placeholder = "Type or paste your text here..."
        self.text_area.insert("1.0", placeholder)
        self.text_area.config(foreground="#4A5568")
        self.text_area.tag_remove("error", "1.0", "end")
        self.issues.clear()
        self.status_label.config(
            text="Ready to check your text",
            foreground="#6B7280"
        )

    def run(self):
        self.root.mainloop()