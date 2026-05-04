import customtkinter as ctk
from tkinter import messagebox
import threading
import os
import sys

# ---------- Appearance --------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_TITLE   = "Spam Email Detector"
APP_VERSION = "v1.2.0"

COLOR_BG      = "#1a1a2e"
COLOR_SIDEBAR = "#16213e"
COLOR_CARD    = "#0f3460"
COLOR_ACCENT  = "#2196F3"
COLOR_SPAM    = "#e53935"
COLOR_HAM     = "#43a047"
COLOR_WARN    = "#fb8c00"
COLOR_TEXT    = "#e0e0e0"
COLOR_SUBTEXT = "#9e9e9e"
COLOR_BORDER  = "#1e3a5f"

MODEL_FILES = [
    'models/vectorizer.pkl', 'models/naive_bayes.pkl',
    'models/svm.pkl',        'models/neural_network.pkl',
]


# ---------- Helpers -----------------------------------------------------
def resource_path(relative_path):
    base = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base, relative_path)


def models_exist() -> bool:
    return all(os.path.exists(p) for p in MODEL_FILES)


# ---------- Main Application --------------------------------------------
class SpamDetectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE}  {APP_VERSION}")
        self.geometry("1100x700")
        self.minsize(950, 600)
        self.configure(fg_color=COLOR_BG)
        self.resizable(True, True)

        self._selected_model = ctk.StringVar(value='svm')
        self._current_view   = ctk.StringVar(value='analysis')

        self._build_layout()

    # ---------- Layout --------------------------------------------------
    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main_container()

    # ---------- Sidebar -------------------------------------------------
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLOR_SIDEBAR)
        sidebar.grid(row=0, column=0, sticky='nsew')
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(10, weight=1)

        ctk.CTkLabel(
            sidebar, text="SPAM DETECTOR",
            font=ctk.CTkFont(family='Segoe UI', size=15, weight='bold'),
            text_color=COLOR_ACCENT
        ).grid(row=0, column=0, padx=24, pady=(32, 4), sticky='w')

        ctk.CTkLabel(
            sidebar, text="NLP  &  Machine Learning",
            font=ctk.CTkFont(size=10), text_color=COLOR_SUBTEXT
        ).grid(row=1, column=0, padx=24, pady=(0, 20), sticky='w')

        ctk.CTkFrame(sidebar, height=1, fg_color=COLOR_BORDER).grid(
            row=2, column=0, padx=16, sticky='ew')

        # Navigation
        ctk.CTkLabel(
            sidebar, text="NAVIGATION",
            font=ctk.CTkFont(size=10, weight='bold'), text_color=COLOR_SUBTEXT
        ).grid(row=3, column=0, padx=24, pady=(18, 8), sticky='w')

        self._btn_analysis = ctk.CTkButton(
            sidebar, text="  Email Analysis",
            command=lambda: self._switch_view('analysis'),
            height=36, corner_radius=8, anchor='w',
            fg_color=COLOR_ACCENT, hover_color="#1565C0",
            font=ctk.CTkFont(size=12)
        )
        self._btn_analysis.grid(row=4, column=0, padx=16, pady=3, sticky='ew')

        self._btn_reports = ctk.CTkButton(
            sidebar, text="  Model Reports",
            command=lambda: self._switch_view('reports'),
            height=36, corner_radius=8, anchor='w',
            fg_color="#1e3a5f", hover_color="#254e7a",
            font=ctk.CTkFont(size=12)
        )
        self._btn_reports.grid(row=5, column=0, padx=16, pady=3, sticky='ew')

        ctk.CTkFrame(sidebar, height=1, fg_color=COLOR_BORDER).grid(
            row=6, column=0, padx=16, pady=(18, 0), sticky='ew')

        ctk.CTkLabel(
            sidebar, text="SELECT MODEL",
            font=ctk.CTkFont(size=10, weight='bold'), text_color=COLOR_SUBTEXT
        ).grid(row=7, column=0, padx=24, pady=(18, 8), sticky='w')

        models = [
            ("Naive Bayes",            "naive_bayes"),
            ("Support Vector Machine", "svm"),
            ("Neural Network",         "neural_network"),
        ]
        for i, (label, value) in enumerate(models):
            ctk.CTkRadioButton(
                sidebar, text=label, variable=self._selected_model, value=value,
                font=ctk.CTkFont(size=12), text_color=COLOR_TEXT,
                fg_color=COLOR_ACCENT, border_color=COLOR_BORDER
            ).grid(row=8 + i, column=0, padx=28, pady=5, sticky='w')

        ctk.CTkFrame(sidebar, height=1, fg_color=COLOR_BORDER).grid(
            row=11, column=0, padx=16, pady=(18, 0), sticky='ew')

        ctk.CTkButton(
            sidebar, text="Train Models",
            command=self._train_models,
            height=36, fg_color="#1e3a5f", hover_color="#254e7a",
            text_color=COLOR_TEXT, font=ctk.CTkFont(size=12), corner_radius=8,
        ).grid(row=12, column=0, padx=16, pady=10, sticky='ew')

        ctk.CTkLabel(
            sidebar, text=APP_VERSION,
            font=ctk.CTkFont(size=10), text_color=COLOR_SUBTEXT
        ).grid(row=13, column=0, padx=24, pady=(4, 20), sticky='w')

    # ---------- Main Container ------------------------------------------
    def _build_main_container(self):
        self._main = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self._main.grid(row=0, column=1, sticky='nsew')
        self._main.grid_rowconfigure(1, weight=1)
        self._main.grid_columnconfigure(0, weight=1)

        # Header
        self._header = ctk.CTkFrame(self._main, fg_color=COLOR_SIDEBAR, height=64, corner_radius=0)
        self._header.grid(row=0, column=0, sticky='ew')
        self._header.grid_propagate(False)
        self._header.grid_columnconfigure(0, weight=1)

        self._header_label = ctk.CTkLabel(
            self._header, text="Email Analysis",
            font=ctk.CTkFont(family='Segoe UI', size=16, weight='bold'),
            text_color=COLOR_TEXT
        )
        self._header_label.grid(row=0, column=0, padx=28, pady=20, sticky='w')

        # Views
        self._view_analysis = self._build_analysis_view(self._main)
        self._view_reports  = self._build_reports_view(self._main)

        # Status bar
        self._status_label = ctk.CTkLabel(
            self._main, text="Ready",
            font=ctk.CTkFont(size=11), text_color=COLOR_SUBTEXT,
        )
        self._status_label.grid(row=2, column=0, padx=28, pady=(0, 12), sticky='w')

        self._switch_view('analysis')

    # ---------- Analysis View -------------------------------------------
    def _build_analysis_view(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=COLOR_BG)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        content = ctk.CTkFrame(frame, fg_color=COLOR_BG)
        content.grid(row=0, column=0, sticky='nsew', padx=28, pady=24)
        content.grid_rowconfigure(1, weight=1)
        content.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            content, text="Email Content",
            font=ctk.CTkFont(size=13, weight='bold'), text_color=COLOR_TEXT
        ).grid(row=0, column=0, sticky='w', pady=(0, 8))

        self._text_input = ctk.CTkTextbox(
            content, corner_radius=10, fg_color=COLOR_CARD,
            border_color=COLOR_BORDER, border_width=1,
            text_color=COLOR_SUBTEXT,
            font=ctk.CTkFont(family='Segoe UI', size=13), wrap='word',
        )
        self._text_input.grid(row=1, column=0, sticky='nsew')
        self._text_input.insert('0.0', 'Paste or type the email content here...')
        self._text_input.bind('<FocusIn>',  self._clear_placeholder)
        self._text_input.bind('<FocusOut>', self._restore_placeholder)

        btn_row = ctk.CTkFrame(content, fg_color='transparent')
        btn_row.grid(row=2, column=0, sticky='ew', pady=(16, 0))
        btn_row.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            btn_row, text="Analyze", command=self._analyze, height=42,
            font=ctk.CTkFont(size=14, weight='bold'),
            fg_color=COLOR_ACCENT, hover_color="#1565C0", corner_radius=10,
        ).grid(row=0, column=0, sticky='ew')

        ctk.CTkButton(
            btn_row, text="Clear", command=self._clear_all, height=42,
            font=ctk.CTkFont(size=13), fg_color="#1e3a5f",
            hover_color="#254e7a", corner_radius=10, width=100,
        ).grid(row=0, column=1, padx=(10, 0))

        # Result card
        result_card = ctk.CTkFrame(
            content, fg_color=COLOR_CARD, corner_radius=12,
            border_width=1, border_color=COLOR_BORDER,
        )
        result_card.grid(row=3, column=0, sticky='ew', pady=(20, 0))
        result_card.grid_columnconfigure((0, 1), weight=1)

        self._verdict_label = ctk.CTkLabel(
            result_card, text="Awaiting Analysis",
            font=ctk.CTkFont(size=15, weight='bold'), text_color=COLOR_SUBTEXT
        )
        self._verdict_label.grid(row=0, column=0, columnspan=2, pady=(20, 8))

        prob_frame = ctk.CTkFrame(result_card, fg_color='transparent')
        prob_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=32, pady=(0, 8))
        prob_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(prob_frame, text="HAM",  font=ctk.CTkFont(size=10, weight='bold'), text_color=COLOR_HAM).grid(row=0, column=0, sticky='w')
        ctk.CTkLabel(prob_frame, text="SPAM", font=ctk.CTkFont(size=10, weight='bold'), text_color=COLOR_SPAM).grid(row=0, column=1, sticky='w')

        self._ham_bar  = ctk.CTkProgressBar(prob_frame, height=10, corner_radius=6, fg_color="#1e3a5f", progress_color=COLOR_HAM)
        self._spam_bar = ctk.CTkProgressBar(prob_frame, height=10, corner_radius=6, fg_color="#1e3a5f", progress_color=COLOR_SPAM)
        self._ham_bar.set(0)
        self._spam_bar.set(0)
        self._ham_bar.grid(row=1,  column=0, sticky='ew', padx=(0, 8))
        self._spam_bar.grid(row=1, column=1, sticky='ew', padx=(8, 0))

        self._ham_pct  = ctk.CTkLabel(prob_frame, text="--%", font=ctk.CTkFont(size=11), text_color=COLOR_HAM)
        self._spam_pct = ctk.CTkLabel(prob_frame, text="--%", font=ctk.CTkFont(size=11), text_color=COLOR_SPAM)
        self._ham_pct.grid(row=2,  column=0, sticky='w')
        self._spam_pct.grid(row=2, column=1, sticky='w')

        self._model_info_label = ctk.CTkLabel(
            result_card, text="", font=ctk.CTkFont(size=10), text_color=COLOR_SUBTEXT
        )
        self._model_info_label.grid(row=2, column=0, columnspan=2, pady=(4, 16))

        return frame

    # ---------- Reports View --------------------------------------------
    def _build_reports_view(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=COLOR_BG)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(frame, fg_color=COLOR_BG)
        scroll.grid(row=0, column=0, sticky='nsew', padx=28, pady=24)
        scroll.grid_columnconfigure(0, weight=1)

        # Section title
        ctk.CTkLabel(
            scroll, text="Model Performance Reports",
            font=ctk.CTkFont(size=15, weight='bold'), text_color=COLOR_TEXT
        ).grid(row=0, column=0, sticky='w', pady=(0, 4))

        ctk.CTkLabel(
            scroll,
            text="Evaluation results for all trained classifiers on the SMS Spam Collection dataset.",
            font=ctk.CTkFont(size=11), text_color=COLOR_SUBTEXT
        ).grid(row=1, column=0, sticky='w', pady=(0, 20))

        # Metrics table header
        self._metrics_frame = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        self._metrics_frame.grid(row=2, column=0, sticky='ew', pady=(0, 20))
        self._metrics_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

        headers = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score']
        for col, h in enumerate(headers):
            ctk.CTkLabel(
                self._metrics_frame, text=h,
                font=ctk.CTkFont(size=12, weight='bold'), text_color=COLOR_ACCENT
            ).grid(row=0, column=col, padx=12, pady=12, sticky='w')

        ctk.CTkFrame(self._metrics_frame, height=1, fg_color=COLOR_BORDER).grid(
            row=1, column=0, columnspan=5, sticky='ew', padx=8)

        self._metric_rows = []
        model_display = [
            ('Naive Bayes',            'naive_bayes'),
            ('Support Vector Machine', 'svm'),
            ('Neural Network',         'neural_network'),
        ]
        for r_idx, (display_name, _) in enumerate(model_display):
            row_labels = []
            bg = COLOR_CARD if r_idx % 2 == 0 else "#0d2d4f"
            ctk.CTkLabel(
                self._metrics_frame, text=display_name,
                font=ctk.CTkFont(size=12), text_color=COLOR_TEXT
            ).grid(row=r_idx + 2, column=0, padx=12, pady=10, sticky='w')
            for col in range(1, 5):
                lbl = ctk.CTkLabel(
                    self._metrics_frame, text="--",
                    font=ctk.CTkFont(size=12), text_color=COLOR_SUBTEXT
                )
                lbl.grid(row=r_idx + 2, column=col, padx=12, pady=10, sticky='w')
                row_labels.append(lbl)
            self._metric_rows.append(row_labels)

        # Refresh button
        ctk.CTkButton(
            scroll, text="Load / Refresh Results",
            command=self._load_reports,
            height=38, fg_color=COLOR_ACCENT, hover_color="#1565C0",
            corner_radius=8, font=ctk.CTkFont(size=12)
        ).grid(row=3, column=0, sticky='w', pady=(0, 24))

        # Confusion matrices section
        ctk.CTkLabel(
            scroll, text="Confusion Matrices",
            font=ctk.CTkFont(size=13, weight='bold'), text_color=COLOR_TEXT
        ).grid(row=4, column=0, sticky='w', pady=(0, 12))

        self._cm_frame = ctk.CTkFrame(scroll, fg_color='transparent')
        self._cm_frame.grid(row=5, column=0, sticky='ew')
        self._cm_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._cm_labels = []
        cm_titles = ['Naive Bayes', 'Support Vector Machine', 'Neural Network']
        cm_files  = ['models/cm_naive_bayes.png', 'models/cm_svm.png', 'models/cm_neural_network.png']
        for col, (title, _) in enumerate(zip(cm_titles, cm_files)):
            ctk.CTkLabel(
                self._cm_frame, text=title,
                font=ctk.CTkFont(size=11, weight='bold'), text_color=COLOR_SUBTEXT
            ).grid(row=0, column=col, pady=(0, 6))
            img_lbl = ctk.CTkLabel(self._cm_frame, text="[Run training to generate]", text_color=COLOR_SUBTEXT)
            img_lbl.grid(row=1, column=col, padx=6)
            self._cm_labels.append(img_lbl)

        return frame

    # ---------- View Switching ------------------------------------------
    def _switch_view(self, view: str):
        self._view_analysis.grid_forget()
        self._view_reports.grid_forget()

        if view == 'analysis':
            self._view_analysis.grid(row=1, column=0, sticky='nsew')
            self._header_label.configure(text="Email Analysis")
            self._btn_analysis.configure(fg_color=COLOR_ACCENT)
            self._btn_reports.configure(fg_color="#1e3a5f")
        else:
            self._view_reports.grid(row=1, column=0, sticky='nsew')
            self._header_label.configure(text="Model Performance Reports")
            self._btn_reports.configure(fg_color=COLOR_ACCENT)
            self._btn_analysis.configure(fg_color="#1e3a5f")
            self._load_reports()

        self._current_view.set(view)

    # ---------- Load Reports --------------------------------------------
    def _load_reports(self):
        if not models_exist():
            self._set_status("Models not found. Train models first.")
            return

        self._set_status("Loading report data...")
        threading.Thread(target=self._compute_reports, daemon=True).start()

    def _compute_reports(self):
        try:
            from src.preprocess import load_and_preprocess
            from src.predict    import load_model
            from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

            X_train, X_test, y_train, y_test, _ = load_and_preprocess()

            model_keys = ['naive_bayes', 'svm', 'neural_network']
            results = []
            for key in model_keys:
                model, _ = load_model(key)
                y_pred = model.predict(X_test)
                results.append({
                    'accuracy':  accuracy_score(y_test, y_pred),
                    'precision': precision_score(y_test, y_pred),
                    'recall':    recall_score(y_test, y_pred),
                    'f1':        f1_score(y_test, y_pred),
                })

            self.after(0, self._update_metrics_table, results)
            self.after(0, self._load_cm_images)
            self.after(0, self._set_status, "Reports loaded successfully.")
        except Exception as e:
            self.after(0, self._set_status, f"Error: {e}")

    def _update_metrics_table(self, results):
        for row_labels, m in zip(self._metric_rows, results):
            values = [
                f"{m['accuracy']*100:.2f}%",
                f"{m['precision']*100:.2f}%",
                f"{m['recall']*100:.2f}%",
                f"{m['f1']*100:.2f}%",
            ]
            for lbl, val in zip(row_labels, values):
                lbl.configure(text=val, text_color=COLOR_TEXT)

    def _load_cm_images(self):
        try:
            from PIL import Image as PILImage
            cm_files = [
                'reports/cm_naive_bayes.png',
                'reports/cm_svm.png',
                'reports/cm_neural_network.png',
            ]
            for lbl, fpath in zip(self._cm_labels, cm_files):
                if os.path.exists(fpath):
                    img = PILImage.open(fpath).resize((280, 230))
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(280, 230))
                    lbl.configure(image=ctk_img, text="")
                    lbl._ctk_image = ctk_img
        except ImportError:
            self._set_status("Install Pillow to display confusion matrix images: pip install Pillow")

    # ---------- Analysis Logic ------------------------------------------
    def _analyze(self):
        text = self._text_input.get('0.0', 'end').strip()
        placeholder = 'Paste or type the email content here...'
        if not text or text == placeholder:
            messagebox.showwarning("Input Required", "Please enter email content to analyze.")
            return
        if not models_exist():
            messagebox.showerror("Models Not Found", "Trained models not found.\nClick 'Train Models' first.")
            return
        self._set_status("Analyzing...")
        self._verdict_label.configure(text="Analyzing...", text_color=COLOR_SUBTEXT)
        self._ham_bar.set(0)
        self._spam_bar.set(0)
        self._ham_pct.configure(text="--%")
        self._spam_pct.configure(text="--%")
        self._model_info_label.configure(text="")
        threading.Thread(target=self._run_prediction, args=(text,), daemon=True).start()

    def _run_prediction(self, text: str):
        try:
            from src.predict import predict
            result = predict(text, model_name=self._selected_model.get())
            self.after(0, self._show_result, result)
        except Exception as e:
            self.after(0, self._show_error, str(e))

    def _show_result(self, result: dict):
        label      = result['label']
        confidence = result['confidence']
        spam_prob  = result['spam_prob']
        ham_prob   = result['ham_prob']
        model_name = self._selected_model.get().replace('_', ' ').title()
        color = COLOR_SPAM if label == 'Spam' else COLOR_HAM

        self._verdict_label.configure(
            text=f"{label.upper()}  -  {confidence}% Confidence",
            font=ctk.CTkFont(size=16, weight='bold'), text_color=color
        )
        self._ham_bar.set(ham_prob / 100)
        self._spam_bar.set(spam_prob / 100)
        self._ham_pct.configure(text=f"{ham_prob}%")
        self._spam_pct.configure(text=f"{spam_prob}%")
        self._model_info_label.configure(text=f"Model: {model_name}")
        self._set_status(f"Analysis complete  |  Ham: {ham_prob}%  |  Spam: {spam_prob}%")

    def _show_error(self, error: str):
        messagebox.showerror("Prediction Error", f"Prediction failed:\n{error}")
        self._set_status("Error occurred.")
        self._verdict_label.configure(text="Analysis failed.", text_color=COLOR_SPAM)

    def _train_models(self):
        self._set_status("Training models... this may take a minute.")
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
        self._verdict_label.configure(
            text="Awaiting Analysis",
            font=ctk.CTkFont(size=15, weight='bold'), text_color=COLOR_SUBTEXT
        )
        self._ham_bar.set(0)
        self._spam_bar.set(0)
        self._ham_pct.configure(text="--%")
        self._spam_pct.configure(text="--%")
        self._model_info_label.configure(text="")
        self._set_status("Ready")

    def _clear_placeholder(self, event):
        if self._text_input.get('0.0', 'end').strip() == 'Paste or type the email content here...':
            self._text_input.delete('0.0', 'end')
            self._text_input.configure(text_color=COLOR_TEXT)

    def _restore_placeholder(self, event):
        if not self._text_input.get('0.0', 'end').strip():
            self._text_input.insert('0.0', 'Paste or type the email content here...')
            self._text_input.configure(text_color=COLOR_SUBTEXT)

    def _set_status(self, message: str):
        self._status_label.configure(text=message)


# ---------- Entry Point -------------------------------------------------
if __name__ == '__main__':
    app = SpamDetectorApp()
    app.mainloop()
