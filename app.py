import customtkinter as ctk
from tkinter import messagebox
import threading
import os
import sys

# ---------- Version -----------------------------------------------------
APP_TITLE   = "Spam Email Detector"
APP_VERSION = "v1.3.0"

# ---------- Theme Palettes ----------------------------------------------
THEME = {
    "dark": {
        "bg":        "#0f1117",
        "sidebar":   "#1a1f2e",
        "card":      "#1e2535",
        "card2":     "#242b3d",
        "border":    "#2a3352",
        "accent":    "#4f8ef7",
        "accent_hv": "#3a78e0",
        "spam":      "#f05454",
        "ham":       "#3dcfa0",
        "warn":      "#f5a623",
        "text":      "#e8eaf6",
        "subtext":   "#7986cb",
        "divider":   "#2a3352",
        "btn_sec":   "#1e2a45",
        "btn_sec_hv":"#253352",
        "nav_active":"#4f8ef7",
        "nav_idle":  "#1e2a45",
    },
    "light": {
        "bg":        "#f0f2f8",
        "sidebar":   "#ffffff",
        "card":      "#ffffff",
        "card2":     "#f5f7ff",
        "border":    "#dde3f5",
        "accent":    "#4f8ef7",
        "accent_hv": "#3a78e0",
        "spam":      "#e53935",
        "ham":       "#2e9e72",
        "warn":      "#f57c00",
        "text":      "#1a1f3c",
        "subtext":   "#5c6bc0",
        "divider":   "#dde3f5",
        "btn_sec":   "#e8edf8",
        "btn_sec_hv":"#d8e0f5",
        "nav_active":"#4f8ef7",
        "nav_idle":  "#e8edf8",
    },
}

MODEL_FILES = [
    'models/vectorizer.pkl', 'models/naive_bayes.pkl',
    'models/svm.pkl',        'models/neural_network.pkl',
]


# ---------- Helpers -----------------------------------------------------
def resource_path(rel):
    base = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base, rel)

def models_exist():
    return all(os.path.exists(p) for p in MODEL_FILES)


# ---------- Application -------------------------------------------------
class SpamDetectorApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self._mode = "dark"
        self._apply_ctk_mode()
        self.title(f"{APP_TITLE}  {APP_VERSION}")
        self.geometry("1120x720")
        self.minsize(960, 620)
        self.resizable(True, True)

        self._selected_model = ctk.StringVar(value='svm')
        self._current_view   = "analysis"

        self._build_ui()

    # ---------- Theme ---------------------------------------------------
    @property
    def C(self):
        return THEME[self._mode]

    def _apply_ctk_mode(self):
        ctk.set_appearance_mode(self._mode)
        ctk.set_default_color_theme("blue")

    def _toggle_theme(self):
        self._mode = "light" if self._mode == "dark" else "dark"
        ctk.set_appearance_mode(self._mode)
        label = "Dark Mode" if self._mode == "light" else "Light Mode"
        self._theme_btn.configure(text=label)
        self._repaint()

    def _repaint(self):
        """Re-apply all dynamic colors after theme switch."""
        C = self.C
        self.configure(fg_color=C["bg"])
        self._sidebar.configure(fg_color=C["sidebar"])
        self._div1.configure(fg_color=C["divider"])
        self._div2.configure(fg_color=C["divider"])
        self._div3.configure(fg_color=C["divider"])
        self._app_title_lbl.configure(text_color=C["accent"])
        self._app_sub_lbl.configure(text_color=C["subtext"])
        self._nav_lbl.configure(text_color=C["subtext"])
        self._model_lbl.configure(text_color=C["subtext"])
        self._theme_btn.configure(fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"], text_color=C["text"])
        self._train_btn.configure(fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"], text_color=C["text"])
        self._version_lbl.configure(text_color=C["subtext"])
        self._header_frame.configure(fg_color=C["sidebar"])
        self._header_label.configure(text_color=C["text"])
        self._main_frame.configure(fg_color=C["bg"])
        self._status_label.configure(text_color=C["subtext"])
        # nav buttons
        self._btn_analysis.configure(
            fg_color=C["nav_active"] if self._current_view == "analysis" else C["nav_idle"],
            text_color="#ffffff" if self._current_view == "analysis" else C["text"],
            hover_color=C["accent_hv"]
        )
        self._btn_reports.configure(
            fg_color=C["nav_active"] if self._current_view == "reports" else C["nav_idle"],
            text_color="#ffffff" if self._current_view == "reports" else C["text"],
            hover_color=C["accent_hv"]
        )
        # radio buttons
        for rb in self._radio_buttons:
            rb.configure(text_color=C["text"], fg_color=C["accent"], border_color=C["border"])
        # analysis view
        self._content_frame.configure(fg_color=C["bg"])
        self._email_lbl.configure(text_color=C["text"])
        self._text_input.configure(fg_color=C["card"], border_color=C["border"])
        self._analyze_btn.configure(fg_color=C["accent"], hover_color=C["accent_hv"])
        self._clear_btn.configure(fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"], text_color=C["text"])
        self._result_card.configure(fg_color=C["card"], border_color=C["border"])
        self._verdict_label.configure(text_color=C["subtext"])
        self._ham_lbl.configure(text_color=C["ham"])
        self._spam_lbl.configure(text_color=C["spam"])
        self._ham_pct.configure(text_color=C["ham"])
        self._spam_pct.configure(text_color=C["spam"])
        self._ham_bar.configure(fg_color=C["border"], progress_color=C["ham"])
        self._spam_bar.configure(fg_color=C["border"], progress_color=C["spam"])
        self._model_info_label.configure(text_color=C["subtext"])

    # ---------- Build UI ------------------------------------------------
    def _build_ui(self):
        self.configure(fg_color=self.C["bg"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

    # ---------- Sidebar -------------------------------------------------
    def _build_sidebar(self):
        C = self.C
        self._sidebar = ctk.CTkFrame(
            self, width=256, corner_radius=0,
            fg_color=C["sidebar"],
            border_width=1, border_color=C["border"]
        )
        self._sidebar.grid(row=0, column=0, sticky='nsew')
        self._sidebar.grid_propagate(False)
        self._sidebar.grid_rowconfigure(12, weight=1)
        self._sidebar.grid_columnconfigure(0, weight=1)

        # App identity
        self._app_title_lbl = ctk.CTkLabel(
            self._sidebar, text="SPAM DETECTOR",
            font=ctk.CTkFont(family='Segoe UI', size=14, weight='bold'),
            text_color=C["accent"]
        )
        self._app_title_lbl.grid(row=0, column=0, padx=20, pady=(28, 2), sticky='w')

        self._app_sub_lbl = ctk.CTkLabel(
            self._sidebar, text="NLP & Machine Learning",
            font=ctk.CTkFont(size=10), text_color=C["subtext"]
        )
        self._app_sub_lbl.grid(row=1, column=0, padx=20, pady=(0, 18), sticky='w')

        self._div1 = ctk.CTkFrame(self._sidebar, height=1, fg_color=C["divider"])
        self._div1.grid(row=2, column=0, padx=16, sticky='ew')

        # Navigation
        self._nav_lbl = ctk.CTkLabel(
            self._sidebar, text="NAVIGATION",
            font=ctk.CTkFont(size=9, weight='bold'), text_color=C["subtext"]
        )
        self._nav_lbl.grid(row=3, column=0, padx=20, pady=(16, 6), sticky='w')

        self._btn_analysis = ctk.CTkButton(
            self._sidebar, text="  Email Analysis",
            command=lambda: self._switch_view('analysis'),
            height=38, corner_radius=8, anchor='w',
            fg_color=C["nav_active"], hover_color=C["accent_hv"],
            text_color="#ffffff", font=ctk.CTkFont(size=12, weight='bold')
        )
        self._btn_analysis.grid(row=4, column=0, padx=14, pady=3, sticky='ew')

        self._btn_reports = ctk.CTkButton(
            self._sidebar, text="  Model Reports",
            command=lambda: self._switch_view('reports'),
            height=38, corner_radius=8, anchor='w',
            fg_color=C["nav_idle"], hover_color=C["accent_hv"],
            text_color=C["text"], font=ctk.CTkFont(size=12)
        )
        self._btn_reports.grid(row=5, column=0, padx=14, pady=3, sticky='ew')

        self._div2 = ctk.CTkFrame(self._sidebar, height=1, fg_color=C["divider"])
        self._div2.grid(row=6, column=0, padx=16, pady=(16, 0), sticky='ew')

        # Model selection
        self._model_lbl = ctk.CTkLabel(
            self._sidebar, text="SELECT MODEL",
            font=ctk.CTkFont(size=9, weight='bold'), text_color=C["subtext"]
        )
        self._model_lbl.grid(row=7, column=0, padx=20, pady=(16, 8), sticky='w')

        self._radio_buttons = []
        models = [
            ("Naive Bayes",            "naive_bayes"),
            ("Support Vector Machine", "svm"),
            ("Neural Network",         "neural_network"),
        ]
        for i, (label, value) in enumerate(models):
            rb = ctk.CTkRadioButton(
                self._sidebar, text=label,
                variable=self._selected_model, value=value,
                font=ctk.CTkFont(size=12), text_color=C["text"],
                fg_color=C["accent"], border_color=C["border"]
            )
            rb.grid(row=8 + i, column=0, padx=26, pady=5, sticky='w')
            self._radio_buttons.append(rb)

        self._div3 = ctk.CTkFrame(self._sidebar, height=1, fg_color=C["divider"])
        self._div3.grid(row=13, column=0, padx=16, pady=(14, 0), sticky='ew')

        # Theme toggle
        self._theme_btn = ctk.CTkButton(
            self._sidebar, text="Light Mode",
            command=self._toggle_theme, height=34,
            fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"],
            text_color=C["text"], font=ctk.CTkFont(size=11), corner_radius=8,
        )
        self._theme_btn.grid(row=14, column=0, padx=14, pady=(10, 4), sticky='ew')

        # Train button
        self._train_btn = ctk.CTkButton(
            self._sidebar, text="Train Models",
            command=self._train_models, height=34,
            fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"],
            text_color=C["text"], font=ctk.CTkFont(size=11), corner_radius=8,
        )
        self._train_btn.grid(row=15, column=0, padx=14, pady=4, sticky='ew')

        self._version_lbl = ctk.CTkLabel(
            self._sidebar, text=APP_VERSION,
            font=ctk.CTkFont(size=9), text_color=C["subtext"]
        )
        self._version_lbl.grid(row=16, column=0, padx=20, pady=(4, 20), sticky='w')

    # ---------- Main Container ------------------------------------------
    def _build_main(self):
        C = self.C
        self._main_frame = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        self._main_frame.grid(row=0, column=1, sticky='nsew')
        self._main_frame.grid_rowconfigure(1, weight=1)
        self._main_frame.grid_columnconfigure(0, weight=1)

        # Top header bar
        self._header_frame = ctk.CTkFrame(
            self._main_frame, fg_color=C["sidebar"], height=60, corner_radius=0,
            border_width=0
        )
        self._header_frame.grid(row=0, column=0, sticky='ew')
        self._header_frame.grid_propagate(False)
        self._header_frame.grid_columnconfigure(0, weight=1)

        self._header_label = ctk.CTkLabel(
            self._header_frame, text="Email Analysis",
            font=ctk.CTkFont(family='Segoe UI', size=15, weight='bold'),
            text_color=C["text"]
        )
        self._header_label.grid(row=0, column=0, padx=32, pady=18, sticky='w')

        # Views
        self._view_analysis = self._build_analysis_view(self._main_frame)
        self._view_reports  = self._build_reports_view(self._main_frame)

        # Status bar
        self._status_label = ctk.CTkLabel(
            self._main_frame, text="Ready",
            font=ctk.CTkFont(size=10), text_color=C["subtext"],
        )
        self._status_label.grid(row=2, column=0, padx=32, pady=(2, 10), sticky='w')

        self._switch_view('analysis')

    # ---------- Analysis View -------------------------------------------
    def _build_analysis_view(self, parent):
        C = self.C
        frame = ctk.CTkFrame(parent, fg_color=C["bg"])
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self._content_frame = ctk.CTkFrame(frame, fg_color=C["bg"])
        self._content_frame.grid(row=0, column=0, sticky='nsew', padx=32, pady=24)
        self._content_frame.grid_rowconfigure(1, weight=1)
        self._content_frame.grid_columnconfigure(0, weight=1)

        self._email_lbl = ctk.CTkLabel(
            self._content_frame, text="Email Content",
            font=ctk.CTkFont(size=12, weight='bold'), text_color=C["text"]
        )
        self._email_lbl.grid(row=0, column=0, sticky='w', pady=(0, 8))

        self._text_input = ctk.CTkTextbox(
            self._content_frame, corner_radius=10,
            fg_color=C["card"], border_color=C["border"], border_width=1,
            text_color=C["subtext"],
            font=ctk.CTkFont(family='Segoe UI', size=13), wrap='word',
        )
        self._text_input.grid(row=1, column=0, sticky='nsew')
        self._text_input.insert('0.0', 'Paste or type the email content here...')
        self._text_input.bind('<FocusIn>',  self._clear_placeholder)
        self._text_input.bind('<FocusOut>', self._restore_placeholder)

        # Buttons row
        btn_row = ctk.CTkFrame(self._content_frame, fg_color='transparent')
        btn_row.grid(row=2, column=0, sticky='ew', pady=(14, 0))
        btn_row.grid_columnconfigure(0, weight=1)

        self._analyze_btn = ctk.CTkButton(
            btn_row, text="Analyze", command=self._analyze, height=44,
            font=ctk.CTkFont(size=14, weight='bold'),
            fg_color=C["accent"], hover_color=C["accent_hv"], corner_radius=10,
        )
        self._analyze_btn.grid(row=0, column=0, sticky='ew')

        self._clear_btn = ctk.CTkButton(
            btn_row, text="Clear", command=self._clear_all, height=44,
            font=ctk.CTkFont(size=12),
            fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"],
            text_color=C["text"], corner_radius=10, width=110,
        )
        self._clear_btn.grid(row=0, column=1, padx=(10, 0))

        # Result card
        self._result_card = ctk.CTkFrame(
            self._content_frame, fg_color=C["card"], corner_radius=12,
            border_width=1, border_color=C["border"],
        )
        self._result_card.grid(row=3, column=0, sticky='ew', pady=(18, 0))
        self._result_card.grid_columnconfigure((0, 1), weight=1)

        self._verdict_label = ctk.CTkLabel(
            self._result_card, text="Awaiting Analysis",
            font=ctk.CTkFont(size=15, weight='bold'), text_color=C["subtext"]
        )
        self._verdict_label.grid(row=0, column=0, columnspan=2, pady=(22, 10))

        prob_frame = ctk.CTkFrame(self._result_card, fg_color='transparent')
        prob_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=36, pady=(0, 6))
        prob_frame.grid_columnconfigure((0, 1), weight=1)

        self._ham_lbl  = ctk.CTkLabel(prob_frame, text="HAM",  font=ctk.CTkFont(size=10, weight='bold'), text_color=C["ham"])
        self._spam_lbl = ctk.CTkLabel(prob_frame, text="SPAM", font=ctk.CTkFont(size=10, weight='bold'), text_color=C["spam"])
        self._ham_lbl.grid(row=0,  column=0, sticky='w')
        self._spam_lbl.grid(row=0, column=1, sticky='w')

        self._ham_bar  = ctk.CTkProgressBar(prob_frame, height=12, corner_radius=6, fg_color=C["border"], progress_color=C["ham"])
        self._spam_bar = ctk.CTkProgressBar(prob_frame, height=12, corner_radius=6, fg_color=C["border"], progress_color=C["spam"])
        self._ham_bar.set(0)
        self._spam_bar.set(0)
        self._ham_bar.grid(row=1,  column=0, sticky='ew', padx=(0, 10))
        self._spam_bar.grid(row=1, column=1, sticky='ew', padx=(10, 0))

        self._ham_pct  = ctk.CTkLabel(prob_frame, text="--%", font=ctk.CTkFont(size=11), text_color=C["ham"])
        self._spam_pct = ctk.CTkLabel(prob_frame, text="--%", font=ctk.CTkFont(size=11), text_color=C["spam"])
        self._ham_pct.grid(row=2,  column=0, sticky='w', pady=(2, 0))
        self._spam_pct.grid(row=2, column=1, sticky='w', pady=(2, 0))

        self._model_info_label = ctk.CTkLabel(
            self._result_card, text="",
            font=ctk.CTkFont(size=10), text_color=C["subtext"]
        )
        self._model_info_label.grid(row=2, column=0, columnspan=2, pady=(6, 18))

        return frame

    # ---------- Reports View --------------------------------------------
    def _build_reports_view(self, parent):
        C = self.C
        frame = ctk.CTkFrame(parent, fg_color=C["bg"])
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(frame, fg_color=C["bg"])
        scroll.grid(row=0, column=0, sticky='nsew', padx=32, pady=24)
        scroll.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            scroll, text="Model Performance Reports",
            font=ctk.CTkFont(size=15, weight='bold'), text_color=C["text"]
        ).grid(row=0, column=0, sticky='w', pady=(0, 4))

        ctk.CTkLabel(
            scroll,
            text="Evaluation results for all trained classifiers on the SMS Spam Collection dataset.",
            font=ctk.CTkFont(size=11), text_color=C["subtext"]
        ).grid(row=1, column=0, sticky='w', pady=(0, 16))

        # Metrics table
        self._metrics_frame = ctk.CTkFrame(
            scroll, fg_color=C["card"], corner_radius=10,
            border_width=1, border_color=C["border"]
        )
        self._metrics_frame.grid(row=2, column=0, sticky='ew', pady=(0, 16))
        self._metrics_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

        for col, h in enumerate(['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score']):
            ctk.CTkLabel(
                self._metrics_frame, text=h,
                font=ctk.CTkFont(size=11, weight='bold'), text_color=C["accent"]
            ).grid(row=0, column=col, padx=14, pady=12, sticky='w')

        ctk.CTkFrame(self._metrics_frame, height=1, fg_color=C["divider"]).grid(
            row=1, column=0, columnspan=5, sticky='ew', padx=10)

        self._metric_rows = []
        for r_idx, display_name in enumerate(['Naive Bayes', 'Support Vector Machine', 'Neural Network']):
            bg = C["card"] if r_idx % 2 == 0 else C["card2"]
            ctk.CTkLabel(
                self._metrics_frame, text=display_name,
                font=ctk.CTkFont(size=12), text_color=C["text"]
            ).grid(row=r_idx + 2, column=0, padx=14, pady=10, sticky='w')
            row_labels = []
            for col in range(1, 5):
                lbl = ctk.CTkLabel(
                    self._metrics_frame, text="--",
                    font=ctk.CTkFont(size=12), text_color=C["subtext"]
                )
                lbl.grid(row=r_idx + 2, column=col, padx=14, pady=10, sticky='w')
                row_labels.append(lbl)
            self._metric_rows.append(row_labels)

        ctk.CTkButton(
            scroll, text="Load / Refresh Results",
            command=self._load_reports, height=38,
            fg_color=C["accent"], hover_color=C["accent_hv"],
            corner_radius=8, font=ctk.CTkFont(size=12)
        ).grid(row=3, column=0, sticky='w', pady=(0, 24))

        ctk.CTkLabel(
            scroll, text="Confusion Matrices",
            font=ctk.CTkFont(size=13, weight='bold'), text_color=C["text"]
        ).grid(row=4, column=0, sticky='w', pady=(0, 12))

        self._cm_frame = ctk.CTkFrame(scroll, fg_color='transparent')
        self._cm_frame.grid(row=5, column=0, sticky='ew')
        self._cm_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._cm_labels = []
        for col, title in enumerate(['Naive Bayes', 'Support Vector Machine', 'Neural Network']):
            ctk.CTkLabel(
                self._cm_frame, text=title,
                font=ctk.CTkFont(size=11, weight='bold'), text_color=C["subtext"]
            ).grid(row=0, column=col, pady=(0, 6))
            img_lbl = ctk.CTkLabel(
                self._cm_frame, text="Run training to generate",
                text_color=C["subtext"], font=ctk.CTkFont(size=10)
            )
            img_lbl.grid(row=1, column=col, padx=6)
            self._cm_labels.append(img_lbl)

        return frame

    # ---------- View Switching ------------------------------------------
    def _switch_view(self, view: str):
        C = self.C
        self._view_analysis.grid_forget()
        self._view_reports.grid_forget()

        if view == 'analysis':
            self._view_analysis.grid(row=1, column=0, sticky='nsew')
            self._header_label.configure(text="Email Analysis")
            self._btn_analysis.configure(fg_color=C["nav_active"], text_color="#ffffff", font=ctk.CTkFont(size=12, weight='bold'))
            self._btn_reports.configure(fg_color=C["nav_idle"],   text_color=C["text"],  font=ctk.CTkFont(size=12))
        else:
            self._view_reports.grid(row=1, column=0, sticky='nsew')
            self._header_label.configure(text="Model Performance Reports")
            self._btn_reports.configure(fg_color=C["nav_active"],  text_color="#ffffff", font=ctk.CTkFont(size=12, weight='bold'))
            self._btn_analysis.configure(fg_color=C["nav_idle"],   text_color=C["text"],  font=ctk.CTkFont(size=12))
            self._load_reports()

        self._current_view = view

    # ---------- Reports Logic -------------------------------------------
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
            self.after(0, self._set_status, f"Error loading reports: {e}")

    def _update_metrics_table(self, results):
        C = self.C
        for row_labels, m in zip(self._metric_rows, results):
            values = [
                f"{m['accuracy']*100:.2f}%",
                f"{m['precision']*100:.2f}%",
                f"{m['recall']*100:.2f}%",
                f"{m['f1']*100:.2f}%",
            ]
            for lbl, val in zip(row_labels, values):
                lbl.configure(text=val, text_color=C["text"])

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
                    img = PILImage.open(fpath).resize((290, 240))
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(290, 240))
                    lbl.configure(image=ctk_img, text="")
                    lbl._ctk_image = ctk_img
        except ImportError:
            self._set_status("Pillow not installed. Run: pip install Pillow")

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
        self._verdict_label.configure(text="Analyzing...", text_color=self.C["subtext"],
                                       font=ctk.CTkFont(size=13))
        self._ham_bar.set(0)
        self._spam_bar.set(0)
        self._ham_pct.configure(text="--%")
        self._spam_pct.configure(text="--%")
        self._model_info_label.configure(text="")
        threading.Thread(target=self._run_prediction, args=(text,), daemon=True).start()

    def _run_prediction(self, text):
        try:
            from src.predict import predict
            result = predict(text, model_name=self._selected_model.get())
            self.after(0, self._show_result, result)
        except Exception as e:
            self.after(0, self._show_error, str(e))

    def _show_result(self, result):
        C = self.C
        label      = result['label']
        confidence = result['confidence']
        spam_prob  = result['spam_prob']
        ham_prob   = result['ham_prob']
        model_name = self._selected_model.get().replace('_', ' ').title()
        color = C["spam"] if label == 'Spam' else C["ham"]

        self._verdict_label.configure(
            text=f"{label.upper()}   {confidence}% Confidence",
            font=ctk.CTkFont(size=17, weight='bold'), text_color=color
        )
        self._ham_bar.set(ham_prob / 100)
        self._spam_bar.set(spam_prob / 100)
        self._ham_pct.configure(text=f"{ham_prob}%")
        self._spam_pct.configure(text=f"{spam_prob}%")
        self._model_info_label.configure(text=f"Model: {model_name}")
        self._set_status(f"Analysis complete  |  Ham: {ham_prob}%  |  Spam: {spam_prob}%")

    def _show_error(self, error):
        messagebox.showerror("Prediction Error", f"Prediction failed:\n{error}")
        self._set_status("Error occurred.")
        self._verdict_label.configure(text="Analysis failed.", text_color=self.C["spam"])

    def _train_models(self):
        self._set_status("Training models... this may take a minute.")
        threading.Thread(target=self._run_training, daemon=True).start()

    def _run_training(self):
        try:
            from src.train import train_all
            train_all()
            self.after(0, self._set_status, "All models trained successfully.")
            self.after(0, messagebox.showinfo, "Done", "All 3 models trained and saved.")
        except Exception as e:
            self.after(0, messagebox.showerror, "Training Error", str(e))
            self.after(0, self._set_status, "Training failed.")

    def _clear_all(self):
        self._text_input.delete('0.0', 'end')
        self._text_input.insert('0.0', 'Paste or type the email content here...')
        self._text_input.configure(text_color=self.C["subtext"])
        self._verdict_label.configure(
            text="Awaiting Analysis",
            font=ctk.CTkFont(size=15, weight='bold'),
            text_color=self.C["subtext"]
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
            self._text_input.configure(text_color=self.C["text"])

    def _restore_placeholder(self, event):
        if not self._text_input.get('0.0', 'end').strip():
            self._text_input.insert('0.0', 'Paste or type the email content here...')
            self._text_input.configure(text_color=self.C["subtext"])

    def _set_status(self, message):
        self._status_label.configure(text=message)


# ---------- Entry Point -------------------------------------------------
if __name__ == '__main__':
    app = SpamDetectorApp()
    app.mainloop()
