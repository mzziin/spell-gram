# ui/main_window.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from services.checker_service import CheckerService
from ui.result_view import highlight_errors, clear_highlights
from core.models import Issue


class MainWindow:
    def __init__(self):
        # Create themed window
        self.root = tb.Window(themename="darkly")
        self.root.title("SpellGram - Advanced Grammar Checker")
        self.root.geometry("1200x800")

        # Make responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Initialize service
        self.service = CheckerService()
        self.issues: list[Issue] = []
        self.is_checking = False
        self.is_fixing = False

        self.create_widgets()

        # Handle cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Main container
        main_frame = tb.Frame(self.root, bootstyle="dark")
        main_frame.grid(row=0, column=0, sticky="nsew")

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)  # header
        main_frame.rowconfigure(1, weight=1)  # text area
        main_frame.rowconfigure(2, weight=0)  # buttons
        main_frame.rowconfigure(3, weight=0)  # status

        # Header
        header_frame = tb.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(80, 0))
        header_frame.columnconfigure(0, weight=1)

        title_container = tb.Frame(header_frame, bootstyle="dark")
        title_container.grid(row=0, column=0)

        title_label = tb.Label(
            title_container,
            text="SpellGram",
            font=("Segoe UI", 46, "bold"),
        )
        title_label.pack(side="left")

        subtitle_label = tb.Label(
            header_frame,
            text="Advanced Offline Grammar & Spell Checker",
            font=("Segoe UI", 12),
            bootstyle="secondary",
        )
        subtitle_label.grid(row=1, column=0, pady=(5, 0))

        # Text area container
        text_container = tb.Frame(main_frame, bootstyle="dark")
        text_container.grid(row=1, column=0, sticky="nsew", padx=120, pady=(50, 40))
        text_container.columnconfigure(0, weight=1)
        text_container.rowconfigure(0, weight=1)

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
            highlightcolor="#FF8C42",
        )
        self.text_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Placeholder functionality
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

        # Scrollbar
        scrollbar = tb.Scrollbar(
            text_frame, command=self.text_area.yview, bootstyle="rounded"
        )
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(5, 5))
        self.text_area.config(yscrollcommand=scrollbar.set)

        # Button panel
        button_container = tb.Frame(main_frame)
        button_container.grid(row=2, column=0, pady=(0, 40))

        self.check_btn = tb.Button(
            button_container,
            text="🔍 Check Text",
            bootstyle="warning-outline",
            width=18,
            command=self.check_text,
        )
        self.check_btn.grid(row=0, column=0, padx=12)

        self.fix_btn = tb.Button(
            button_container,
            text="✓ Fix All Errors",
            bootstyle="success-outline",
            width=18,
            command=self.fix_text,
            state="disabled",
        )
        self.fix_btn.grid(row=0, column=1, padx=12)

        clear_btn = tb.Button(
            button_container,
            text="⟲ Clear",
            bootstyle="outline",
            width=18,
            command=self.clear_text,
        )
        clear_btn.grid(row=0, column=2, padx=12)

        # Status bar with progress indicator
        status_container = tb.Frame(main_frame, bootstyle="dark")
        status_container.grid(row=3, column=0, sticky="ew", pady=(0, 30))
        status_container.columnconfigure(0, weight=1)

        self.status_label = tb.Label(
            status_container,
            text="Ready to check your text",
            font=("Segoe UI", 12),
            bootstyle="secondary",
        )
        self.status_label.grid(row=0, column=0, pady=5)

        # Progress bar (hidden by default)
        self.progress = tb.Progressbar(
            status_container,
            mode="indeterminate",
            bootstyle="warning-striped",
            length=300,
        )
        self.progress.grid(row=1, column=0, pady=5)
        self.progress.grid_remove()

    # ============== Event Handlers ==============

    def check_text(self):
        """Run spell and grammar checks."""
        if self.is_checking:
            return

        text = self.text_area.get("1.0", "end-1c").strip()
        placeholder = "Type or paste your text here..."

        if not text or text == placeholder:
            messagebox.showinfo("Info", "Please enter some text to check.")
            return

        # Clear previous highlights
        clear_highlights(self.text_area)
        self.issues.clear()

        # Update UI
        self.is_checking = True
        self.check_btn.config(state="disabled")
        self.fix_btn.config(state="disabled")
        self.status_label.config(text="🔄 Checking text...", foreground="#F59E0B")
        self.progress.grid()
        self.progress.start(10)

        # Run check in background
        self.service.check_text(text, callback=self.on_check_complete)

    def on_check_complete(self, issues, error):
        """Called when background check completes."""
        # Schedule UI update on main thread
        self.root.after(0, self._update_check_ui, issues, error)

    def _update_check_ui(self, issues, error):
        """Update UI after check completes (main thread)."""
        self.progress.stop()
        self.progress.grid_remove()
        self.is_checking = False
        self.check_btn.config(state="normal")

        if error:
            self.status_label.config(text=f"❌ Error: {error}", foreground="#EF4444")
            messagebox.showerror("Check Error", f"An error occurred:\n{error}")
            return

        self.issues = issues

        if not issues:
            self.status_label.config(
                text="✨ Perfect! No errors found", foreground="#10B981"
            )
            messagebox.showinfo("Check Complete", "No errors found!")
            return

        # Highlight errors
        highlight_errors(self.text_area, issues)

        # Count error types
        spelling_count = sum(1 for i in issues if i.type == "spelling")
        grammar_count = len(issues) - spelling_count

        status_parts = []
        if spelling_count:
            status_parts.append(f"{spelling_count} spelling")
        if grammar_count:
            status_parts.append(f"{grammar_count} grammar")

        status_text = f"⚠️ Found {' and '.join(status_parts)} issue"
        if len(issues) > 1:
            status_text += "s"

        self.status_label.config(text=status_text, foreground="#F59E0B")
        self.fix_btn.config(state="normal")

    def fix_text(self):
        """Apply all corrections automatically."""
        if self.is_fixing or not self.issues:
            return

        # Update UI
        self.is_fixing = True
        self.check_btn.config(state="disabled")
        self.fix_btn.config(state="disabled")
        self.status_label.config(text="🔧 Fixing errors...", foreground="#3B82F6")
        self.progress.grid()
        self.progress.start(10)

        # Get current text
        text = self.text_area.get("1.0", "end-1c")

        # Run fix in background
        self.service.fix_text(text, self.issues, callback=self.on_fix_complete)

    def on_fix_complete(self, corrected_text, error):
        """Called when background fix completes."""
        self.root.after(0, self._update_fix_ui, corrected_text, error)

    def _update_fix_ui(self, corrected_text, error):
        """Update UI after fix completes (main thread)."""
        self.progress.stop()
        self.progress.grid_remove()
        self.is_fixing = False
        self.check_btn.config(state="normal")
        self.fix_btn.config(state="disabled")

        if error:
            self.status_label.config(text=f"❌ Error: {error}", foreground="#EF4444")
            messagebox.showerror("Fix Error", f"An error occurred:\n{error}")
            return

        # Update text
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", corrected_text)

        # Clear highlights and issues
        clear_highlights(self.text_area)
        self.issues.clear()

        self.status_label.config(
            text="✓ All errors fixed successfully!", foreground="#10B981"
        )

        # Optional: Verify fixes
        # Uncomment to re-check after fixing
        # self.root.after(1000, self.verify_fixes)

    def verify_fixes(self):
        """Optional: Re-check text after fixing to verify."""
        text = self.text_area.get("1.0", "end-1c")
        remaining_issues, error = self.service.verify_fixes(text)

        if remaining_issues:
            self.status_label.config(
                text=f"⚠️ {len(remaining_issues)} issue(s) remain", foreground="#F59E0B"
            )
        else:
            self.status_label.config(
                text="✓ Verification complete - No errors found!", foreground="#10B981"
            )

    def clear_text(self):
        """Clear text area and reset state."""
        self.text_area.delete("1.0", "end")
        placeholder = "Type or paste your text here..."
        self.text_area.insert("1.0", placeholder)
        self.text_area.config(foreground="#4A5568")

        clear_highlights(self.text_area)
        self.issues.clear()

        self.fix_btn.config(state="disabled")
        self.status_label.config(text="Ready to check your text", foreground="#6B7280")

    def on_closing(self):
        """Clean up resources before closing."""
        self.service.close()
        self.root.destroy()

    def run(self):
        """Start the application."""
        self.root.mainloop()
