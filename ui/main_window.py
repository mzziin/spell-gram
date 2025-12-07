import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from services.checker_service import CheckerService
from core.models import Issue


class MainWindow:
    def __init__(self):
        self.root = tb.Window(themename="darkly")
        self.root.title("SpellGram")
        self.root.geometry("1200x800")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.service = CheckerService()
        
        # State management
        self.mode = "spelling"  # "spelling" or "grammar"
        self.spelling_issues: list[Issue] = []
        self.grammar_issues: list[Issue] = []
        self.current_hover_window = None
        self._hide_job = None 

        self.create_widgets()

    def create_widgets(self):
        main_frame = tb.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew")

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)  # header
        main_frame.rowconfigure(1, weight=1)  # text area
        main_frame.rowconfigure(2, weight=0)  # buttons
        main_frame.rowconfigure(3, weight=0)  # status

        # --- Header ---
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

        # --- Text Area ---
        text_container = tb.Frame(main_frame, bootstyle="dark")
        text_container.grid(row=1, column=0, sticky="nsew", padx=120, pady=(70, 70))
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
            highlightcolor="#FF8C42"
        )
        self.text_area.grid(row=0, column=0, sticky="nsew")

        # Placeholder
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

        # Setup error highlighting tags
        self.text_area.tag_config("grammar_error", foreground="orange", underline=1)

        # Scrollbar
        scrollbar = tb.Scrollbar(text_frame, command=self.text_area.yview, bootstyle="rounded")
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(5, 5))
        self.text_area.config(yscrollcommand=scrollbar.set)

        # --- Buttons ---
        button_container = tb.Frame(main_frame)
        button_container.grid(row=2, column=0, pady=(0, 80))

        self.check_btn = tb.Button(
            button_container,
            text="🔍 Check Spelling",
            bootstyle="warning-outline",
            width=20,
            command=self.check_text,
            cursor="hand2"
        )
        self.check_btn.grid(row=0, column=0, padx=12)

        self.fix_btn = tb.Button(
            button_container,
            text="✓ Fix Grammar",
            bootstyle="success-outline",
            width=20,
            command=self.fix_grammar,
            cursor="hand2",
            state="disabled"
        )
        self.fix_btn.grid(row=0, column=1, padx=12)

        clear_btn = tb.Button(
            button_container,
            text="⟲ Clear",
            bootstyle="outline",
            width=20,
            command=self.clear_text,
            cursor="hand2"
        )
        clear_btn.grid(row=0, column=2, padx=12)

        # --- Status Bar ---
        status_container = tb.Frame(main_frame, bootstyle="dark")
        status_container.grid(row=3, column=0, sticky="ew", pady=(0, 30))
        status_container.columnconfigure(0, weight=1)

        self.status_label = tb.Label(
            status_container,
            text="Ready to check spelling",
            font=("Segoe UI", 12),
            bootstyle="primary"
        )
        self.status_label.grid(row=0, column=0, pady=5)


    # ---------------- Core Logic ----------------
    
    def check_text(self):
        """Check spelling or grammar based on current mode."""
        text = self.text_area.get("1.0", "end-1c").strip()
        placeholder = "Type or paste your text here..."
        
        if not text or text == placeholder:
            messagebox.showinfo("Info", "Please enter some text to check.")
            return

        if self.mode == "spelling":
            self.check_spelling(text)
        else:
            self.check_grammar(text)

    def check_spelling(self, text: str):
        """Check for spelling errors."""
        self.spelling_issues = self.service.check_spelling(text)
        
        if not self.spelling_issues:
            # No spelling errors, switch to grammar mode
            self.mode = "grammar"
            self.check_btn.config(text="🔍 Check Grammar")
            self.status_label.config(
                text="✨ Perfect spelling! Click 'Check Grammar' to continue",
                foreground="#10B981"
            )
            return

        # Highlight spelling errors
        self.highlight_spelling_errors()
        
        self.status_label.config(
            text=f"⚠️ Found {len(self.spelling_issues)} spelling error{'s' if len(self.spelling_issues) > 1 else ''}. Hover to see suggestions.",
            foreground="#EF4444"
        )

    def check_grammar(self, text: str):
        """Check for grammar errors."""
        self.grammar_issues = self.service.check_grammar(text)
        
        if not self.grammar_issues:
            self.fix_btn.config(state="disabled")
            self.status_label.config(
                text="✨ Perfect grammar! No errors found",
                foreground="#10B981"
            )
            messagebox.showinfo("Check Complete", "No grammar errors found.")
            return

        # Highlight grammar errors
        self.highlight_grammar_errors()
        
        # Enable fix button
        self.fix_btn.config(state="normal")
        
        self.status_label.config(
            text=f"⚠️ Found {len(self.grammar_issues)} grammar error{'s' if len(self.grammar_issues) > 1 else ''}. Click 'Fix Grammar' to correct.",
            foreground="#F59E0B"
        )

    def highlight_spelling_errors(self):
        """Highlight spelling errors and bind hover events."""
        # Remove all previous tags
        self.text_area.tag_remove("spelling_error", "1.0", "end")
        
        # Remove all previous bindings
        self.text_area.tag_unbind("spelling_error", "<Enter>")
        self.text_area.tag_unbind("spelling_error", "<Leave>")
        
        for issue in self.spelling_issues:
            # Create unique tag for each error
            tag_name = f"spelling_error_{issue.start}_{issue.end}"
            
            start_idx = f"1.0+{issue.start}c"
            end_idx = f"1.0+{issue.end}c"
            
            # Configure the tag with error styling
            self.text_area.tag_config(tag_name, foreground="red", underline=1)
            self.text_area.tag_add(tag_name, start_idx, end_idx)
            
            # Bind hover events for this specific error with unique tag
            self.text_area.tag_bind(
                tag_name, 
                "<Enter>", 
                lambda e, iss=issue: self.show_suggestions(e, iss)
            )
            self.text_area.tag_bind(
                tag_name, 
                "<Leave>", 
                self.hide_suggestions
            )

    def highlight_grammar_errors(self):
        """Highlight grammar errors."""
        self.text_area.tag_remove("grammar_error", "1.0", "end")
        
        for issue in self.grammar_issues:
            start_idx = f"1.0+{issue.start}c"
            end_idx = f"1.0+{issue.end}c"
            self.text_area.tag_add("grammar_error", start_idx, end_idx)

    def show_suggestions(self, event, issue: Issue):
        """Show suggestion popup when hovering over misspelled word."""
        # Close any existing popup
        if self.current_hover_window:
            try:
                self.current_hover_window.destroy()
            except:
                pass
            self.current_hover_window = None
        
        # Verify this issue still exists in our list
        if issue not in self.spelling_issues:
            return
        
        # Create popup window
        popup = tb.Toplevel(self.root)
        popup.wm_overrideredirect(True)
        popup.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        # Make popup stay on top
        popup.wm_attributes("-topmost", True)
        
        # Popup frame with shadow effect
        frame = tb.Frame(popup, relief="solid", borderwidth=2)
        frame.pack(fill="both", expand=True, padx=3, pady=3)
        
        # Title
        title = tb.Label(
            frame, 
            text=f"Suggestions for '{issue.original}':",
            font=("Segoe UI", 10, "bold"),
            bootstyle="light"
        )
        title.pack(padx=10, pady=(10, 5))
        
        # Debug: Show what suggestions we have
        print(f"Word: {issue.original}, Suggestions: {issue.suggestions}")
        
        # Suggestion buttons
        if issue.suggestions and len(issue.suggestions) > 0:
            for i, suggestion in enumerate(issue.suggestions):
                btn = tb.Button(
                    frame,
                    text=f"{i+1}. {suggestion}",
                    bootstyle="info-outline",
                    cursor="hand2",
                    command=lambda s=suggestion, iss=issue, p=popup: self.apply_suggestion(s, iss, p)
                )
                btn.pack(padx=10, pady=3, fill="x")
        else:
            no_sugg = tb.Label(
                frame,
                text="No suggestions available",
                font=("Segoe UI", 9),
                bootstyle="secondary"
            )
            no_sugg.pack(padx=10, pady=5)
        
        self.current_hover_window = popup
        
        # Keep popup alive when mouse enters it
        popup.bind("<Enter>", lambda e: self.keep_popup_alive())
        popup.bind("<Leave>", lambda e: self.schedule_popup_hide())

    def keep_popup_alive(self):
        """Cancel any scheduled popup hide."""
        if hasattr(self, '_hide_job') and self._hide_job:
            try:
                self.root.after_cancel(self._hide_job)
            except:
                pass
            self._hide_job = None

    def schedule_popup_hide(self):
        """Schedule popup to hide after a short delay."""
        if hasattr(self, '_hide_job') and self._hide_job:
            try:
                self.root.after_cancel(self._hide_job)
            except:
                pass
        self._hide_job = self.root.after(200, self.hide_suggestions_delayed)

    def hide_suggestions(self, event):
        """Schedule hiding of suggestion popup with a delay."""
        if hasattr(self, '_hide_job') and self._hide_job:
            try:
                self.root.after_cancel(self._hide_job)
            except:
                pass
        # Give user time to move mouse to popup
        self._hide_job = self.root.after(300, self.hide_suggestions_delayed)

    def hide_suggestions_delayed(self):
        """Actually hide the suggestion popup."""
        if self.current_hover_window:
            try:
                self.current_hover_window.destroy()
            except:
                pass
            self.current_hover_window = None
        if hasattr(self, '_hide_job'):
            self._hide_job = None

    def apply_suggestion(self, chosen_word: str, issue: Issue, popup):
        """Apply the chosen spelling correction."""
        # Close popup immediately
        try:
            popup.destroy()
        except:
            pass
        self.current_hover_window = None
        
        # Cancel any pending hide jobs
        if hasattr(self, '_hide_job') and self._hide_job:
            try:
                self.root.after_cancel(self._hide_job)
            except:
                pass
            self._hide_job = None
        
        # Verify issue still exists
        if issue not in self.spelling_issues:
            return
        
        # Get current text
        text = self.text_area.get("1.0", "end-1c")
        
        # Apply correction
        corrected_text = self.service.apply_spell_correction(text, issue, chosen_word)
        
        # Update text area
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", corrected_text)
        
        # Remove the fixed issue
        self.spelling_issues.remove(issue)
        
        # Adjust positions of remaining issues
        offset = len(chosen_word) - len(issue.original)
        for remaining_issue in self.spelling_issues:
            if remaining_issue.start > issue.start:
                remaining_issue.start += offset
                remaining_issue.end += offset
        
        # Remove all old tags before re-highlighting
        for tag in self.text_area.tag_names():
            if tag.startswith("spelling_error_"):
                self.text_area.tag_delete(tag)
        
        if not self.spelling_issues:
            # All spelling errors fixed, switch to grammar mode
            self.mode = "grammar"
            self.check_btn.config(text="🔍 Check Grammar")
            self.status_label.config(
                text="✨ All spelling errors fixed! Click 'Check Grammar' to continue",
                foreground="#10B981"
            )
        else:
            # Re-highlight remaining errors
            self.highlight_spelling_errors()
            self.status_label.config(
                text=f"⚠️ {len(self.spelling_issues)} spelling error{'s' if len(self.spelling_issues) > 1 else ''} remaining",
                foreground="#EF4444"
            )

    def fix_grammar(self):
        if not self.grammar_issues:
            messagebox.showinfo("Info", "No grammar errors to fix.")
            return
        
        text = self.text_area.get("1.0", "end-1c")
        
        # Apply all grammar corrections
        corrected_text = self.service.fix_grammar(text, self.grammar_issues)
        
        # Update text area
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", corrected_text)
        
        # Remove highlighting
        self.text_area.tag_remove("grammar_error", "1.0", "end")
        
        # Clear issues
        self.grammar_issues.clear()
        
        # Disable fix button
        self.fix_btn.config(state="disabled")
        
        self.status_label.config(
            text="✓ All grammar errors fixed successfully",
            foreground="#10B981"
        )

    def clear_text(self):
        self.text_area.delete("1.0", "end")
        placeholder = "Type or paste your text here..."
        self.text_area.insert("1.0", placeholder)
        self.text_area.config(foreground="#4A5568")
        
        # Remove all tag bindings and tags
        for tag in self.text_area.tag_names():
            if tag.startswith("spelling_error_"):
                self.text_area.tag_delete(tag)
        
        self.text_area.tag_remove("grammar_error", "1.0", "end")
        
        # Clear issues
        self.spelling_issues.clear()
        self.grammar_issues.clear()
        
        # Reset mode
        self.mode = "spelling"
        self.check_btn.config(text="🔍 Check Spelling")
        self.fix_btn.config(state="disabled")
        
        # Hide any popup
        self.hide_suggestions_delayed()
        
        self.status_label.config(
            text="Ready to check spelling",
            foreground="#6B7280"
        )

    def run(self):
        self.root.mainloop()