import customtkinter as ctk
from tkinter import messagebox
import threading
import os
import sys

# ── Appearance ────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_TITLE   = "Spam Email Detector"
APP_VERSION = "v1.0.0"

COLOR_BG        = "#1a1a2e"
COLOR_SIDEBAR   = "#16213e"
COLOR_CARD      = "#0f3460"
COLOR_ACCENT    = "#2196F3"
COLOR_SPAM      = "#e53935"
COLOR_HAM       = "#43a047"
COLOR_TEXT      = "#e0e0e0"
COLOR_SUBTEXT   = "#9e9e9e"
COLOR_BORDER    = "#1e3a5f"


# ── Helpers ───────────────────────────────────────────────────────────────────
def resource_path(relative_path):
    """Handle PyInstaller bundled paths."""
    base = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base, relative_path)


def models_exist() -> bool:
    required = ['models/vectorizer.pkl', 'models/svm.pkl',
                'models/naive_bayes.pkl', 'models/neural_network.pkl']
    return all(os.path.exists(p) for p in required)


# ── Main Application ──────────────────────────────────────────────────────────
class SpamDetectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE}  {APP_VERSION}")
        self.geometry("980x640")
        self.minsize(880, 580)
        self.configure(fg_color=COLOR_BG)
        self.resizable(True, True)

        self._selected_model = ctk.StringVar(value='svm')
        self._result_data    = None

        self._build_layout()

    # ── Layout ─────────────────────────────────────────────────────────────
    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

    # ── Sidebar ────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self, width=230, corner_radius=0,
            fg_color=COLOR_SIDEBAR
        )
        sidebar.grid(row=0, column=0, sticky='nsew')
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(8, weight=1)

        # Logo / App name
        ctk.CTkLabel(
            sidebar,
            text="SPAM DETECTOR",
            font=ctk.CTkFont(family='Segoe UI', size=15, weight='bold'),
            text_color=COLOR_ACCENT
        ).grid(row=0, column=0, padx=24, pady=(32, 4), sticky='w')

        ctk.CTkLabel(
            sidebar,
            text="NLP  &  Machine Learning",
            font=ctk.CTkFont(size=10),
            text_color=COLOR_SUBTEXT
        ).grid(row=1, column=0, padx=24, pady=(0, 28), sticky='w')

        # Separator
        ctk.CTkFrame(sidebar, height=1, fg_color=COLOR_BORDER).grid(
            row=2, column=0, padx=16, sticky='ew'
        )

        # Model selection label
        ctk.CTkLabel(
            sidebar,
            text="SELECT MODEL",
            font=ctk.CTkFont(size=10, weight='bold'),
            text_color=COLOR_SUBTEXT
        ).grid(row=3, column=0, padx=24, pady=(22, 8), sticky='w')

        # Model radio buttons
        models = [
            ("Naive Bayes",     "naive_bayes"),
            ("Support Vector Machine", "svm"),
            ("Neural Network",  "neural_network"),
        ]
        for i, (label, value) in enumerate(models):
            ctk.CTkRadioButton(
                sidebar,
                text=label,
                variable=self._selected_model,
                value=value,
                font=ctk.CTkFont(size=12),
                text_color=COLOR_TEXT,
                fg_color=COLOR_ACCENT,
                border_color=COLOR_BORDER
            ).grid(row=4 + i, column=0, padx=28, pady=6, sticky='w')

        # Separator
        ctk.CTkFrame(sidebar, height=1, fg_color=COLOR_BORDER).grid(
            row=7, column=0, padx=16, pady=(20, 0), sticky='ew'
        )

        # Train button
        ctk.CTkButton(
            sidebar,
            text="  Train Models",
            command=self._train_models,
            height=38,
            fg_color="#1e3a5f",
            hover_color="#254e7a",
            text_color=COLOR_TEXT,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
        ).grid(row=9, column=0, padx=16, pady=8, sticky='ew')

        # Version
        ctk.CTkLabel(
            sidebar,
            text=APP_VERSION,
            font=ctk.CTkFont(size=10),
            text_color=COLOR_SUBTEXT
        ).grid(row=10, column=0, padx=24, pady=(4, 20), sticky='w')

    # ── Main Panel ─────────────────────────────────────────────────────────
    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        main.grid(row=0, column=1, sticky='nsew', padx=0)
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(main, fg_color=COLOR_SIDEBAR, height=64, corner_radius=0)
        header.grid(row=0, column=0, sticky='ew')
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Email Analysis",
            font=ctk.CTkFont(family='Segoe UI', size=16, weight='bold'),
            text_color=COLOR_TEXT
        ).grid(row=0, column=0, padx=28, pady=20, sticky='w')

        # Content area
        content = ctk.CTkFrame(main, fg_color=COLOR_BG)
        content.grid(row=1, column=0, sticky='nsew', padx=28, pady=24)
        content.grid_rowconfigure(1, weight=1)
        content.grid_columnconfigure(0, weight=1)

        # Input label
        ctk.CTkLabel(
            content,
            text="Email Content",
            font=ctk.CTkFont(size=13, weight='bold'),
            text_color=COLOR_TEXT
        ).grid(row=0, column=0, sticky='w', pady=(0, 8))

        # Text input
        self._text_input = ctk.CTkTextbox(
            content,
            corner_radius=10,
            fg_color=COLOR_CARD,
            border_color=COLOR_BORDER,
            border_width=1,
            text_color=COLOR_TEXT,
            font=ctk.CTkFont(family='Segoe UI', size=13),
            wrap='word',
        )
        self._text_input.grid(row=1, column=0, sticky='nsew')
        self._text_input.insert('0.0', 'Paste or type the email content here...')
        self._text_input.bind('<FocusIn>',  self._clear_placeholder)
        self._text_input.bind('<FocusOut>', self._restore_placeholder)

        # Action buttons row
        btn_row = ctk.CTkFrame(content, fg_color='transparent')
        btn_row.grid(row=2, column=0, sticky='ew', pady=(16, 0))
        btn_row.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            btn_row,
            text="Analyze",
            command=self._analyze,
            height=42,
            font=ctk.CTkFont(size=14, weight='bold'),
            fg_color=COLOR_ACCENT,
            hover_color="#1565C0",
            corner_radius=10,
        ).grid(row=0, column=0, sticky='ew')

        ctk.CTkButton(
            btn_row,
            text="Clear",
            command=self._clear_all,
            height=42,
            font=ctk.CTkFont(size=13),
            fg_color="#1e3a5f",
            hover_color="#254e7a",
            corner_radius=10,
            width=100,
        ).grid(row=0, column=1, padx=(10, 0))

        # Result card
        self._result_card = ctk.CTkFrame(
            content,
            fg_color=COLOR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER,
            height=120,
        )
        self._result_card.grid(row=3, column=0, sticky='ew', pady=(20, 0))
        self._result_card.grid_propagate(False)
        self._result_card.grid_columnconfigure(0, weight=1)

        self._result_label = ctk.CTkLabel(
            self._result_card,
            text="No analysis yet. Enter email content and click Analyze.",
            font=ctk.CTkFont(size=13),
            text_color=COLOR_SUBTEXT,
        )
        self._result_label.grid(row=0, column=0, padx=24, pady=20)

        self._confidence_label = ctk.CTkLabel(
            self._result_card,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLOR_SUBTEXT,
        )
        self._confidence_label.grid(row=1, column=0, padx=24, pady=(0, 16))

        # Status bar
        self._status_label = ctk.CTkLabel(
            main,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color=COLOR_SUBTEXT,
        )
        self._status_label.grid(row=2, column=0, padx=28, pady=(0, 12), sticky='w')

    # ── Logic ──────────────────────────────────────────────────────────────
    def _analyze(self):
        text = self._text_input.get('0.0', 'end').strip()
        placeholder = 'Paste or type the email content here...'

        if not text or text == placeholder:
            messagebox.showwarning("Input Required", "Please enter email content to analyze.")
            return

        if not models_exist():
            messagebox.showerror(
                "Models Not Found",
                "Trained models not found.\nPlease click 'Train Models' first."
            )
            return

        self._set_status("Analyzing...")
        self._result_label.configure(text="Analyzing...", text_color=COLOR_SUBTEXT)
        self._confidence_label.configure(text="")

        threading.Thread(target=self._run_prediction, args=(text,), daemon=True).start()

    def _run_prediction(self, text: str):
        try:
            from src.predict import predict
            model_name = self._selected_model.get()
            result = predict(text, model_name=model_name)
            self.after(0, self._show_result, result)
        except Exception as e:
            self.after(0, self._show_error, str(e))

    def _show_result(self, result: dict):
        label      = result['label']
        confidence = result['confidence']
        model_name = self._selected_model.get().replace('_', ' ').title()

        color = COLOR_SPAM if label == 'Spam' else COLOR_HAM
        icon  = '[SPAM]' if label == 'Spam' else '[HAM]'

        self._result_label.configure(
            text=f"{icon}   {label.upper()}",
            font=ctk.CTkFont(size=20, weight='bold'),
            text_color=color
        )
        self._confidence_label.configure(
            text=f"Confidence: {confidence}%    |    Model: {model_name}",
            text_color=COLOR_SUBTEXT
        )
        self._set_status(f"Analysis complete using {model_name}.")

    def _show_error(self, error: str):
        messagebox.showerror("Error", f"Prediction failed:\n{error}")
        self._set_status("Error occurred.")
        self._result_label.configure(
            text="Analysis failed. Check console for details.",
            text_color=COLOR_SPAM
        )

    def _train_models(self):
        self._set_status("Training models... this may take a moment.")
        threading.Thread(target=self._run_training, daemon=True).start()

    def _run_training(self):
        try:
            from src.train import train_all
            train_all()
            self.after(0, self._set_status, "All models trained successfully.")
            self.after(0, messagebox.showinfo, "Done", "All models trained and saved.")
        except Exception as e:
            self.after(0, messagebox.showerror, "Training Error", str(e))
            self.after(0, self._set_status, "Training failed.")

    def _clear_all(self):
        self._text_input.delete('0.0', 'end')
        self._text_input.insert('0.0', 'Paste or type the email content here...')
        self._text_input.configure(text_color=COLOR_SUBTEXT)
        self._result_label.configure(
            text="No analysis yet. Enter email content and click Analyze.",
            font=ctk.CTkFont(size=13),
            text_color=COLOR_SUBTEXT
        )
        self._confidence_label.configure(text="")
        self._set_status("Ready")

    def _clear_placeholder(self, event):
        current = self._text_input.get('0.0', 'end').strip()
        if current == 'Paste or type the email content here...':
            self._text_input.delete('0.0', 'end')
            self._text_input.configure(text_color=COLOR_TEXT)

    def _restore_placeholder(self, event):
        current = self._text_input.get('0.0', 'end').strip()
        if not current:
            self._text_input.insert('0.0', 'Paste or type the email content here...')
            self._text_input.configure(text_color=COLOR_SUBTEXT)

    def _set_status(self, message: str):
        self._status_label.configure(text=message)


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = SpamDetectorApp()
    app.mainloop()
