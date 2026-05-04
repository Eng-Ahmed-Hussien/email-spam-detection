"""
Spam Email Detector  v1.4.2
Fixes: sample card tags, spinner bg, sidebar row layout,
       donut hidden until result, all 3 models selectable.
"""
import customtkinter as ctk
from tkinter import messagebox, Canvas
import threading
import os, sys

# ── Version ──────────────────────────────────────────────────────────────
APP_TITLE   = "Spam Email Detector"
APP_VERSION = "v1.4.2"

TEAM_MEMBERS = [
    "Ahmed Hussien",
    "Mohamed Ali",
    "Sara Khaled",
]

# ── Sample Emails ─────────────────────────────────────────────────────────
# tag: ("SPAM" or "HAM", body_text)
SAMPLE_EMAILS = [
    ("SPAM", "Congratulations! You've been selected to receive a FREE iPhone 15. Click the link NOW to claim your prize before it expires!"),
    ("SPAM", "URGENT: Your bank account has been compromised. Verify your details immediately at secure-bank-login.xyz or your account will be suspended."),
    ("SPAM", "Win $1,000,000 cash! You are our lucky winner this week. Send your name and address to collect your reward. Limited time offer!"),
    ("HAM",  "Hey, are we still on for the meeting tomorrow at 10am? Let me know if you need to reschedule."),
    ("HAM",  "The project report has been uploaded to the shared drive. Please review section 3 and send your feedback by Friday."),
    ("HAM",  "Reminder: Your dentist appointment is confirmed for Thursday at 2:30 PM. Please arrive 10 minutes early."),
]

# ── Theme Palettes ───────────────────────────────────────────────────────
THEME = {
    "dark": {
        "bg":         "#0d1117",
        "sidebar":    "#161b27",
        "card":       "#1c2333",
        "card2":      "#212840",
        "border":     "#2d3a58",
        "accent":     "#4f8ef7",
        "accent_hv":  "#3a78e0",
        "spam":       "#f05454",
        "ham":        "#3ecf8e",
        "warn":       "#f5a623",
        "text":       "#e6edf3",
        "subtext":    "#7d8590",
        "divider":    "#2d3a58",
        "btn_sec":    "#21293d",
        "btn_sec_hv": "#2a3650",
        "nav_active": "#4f8ef7",
        "nav_idle":   "#21293d",
        "footer":     "#111827",
        "donut_bg":   "#2d3a58",
        "loader":     "#4f8ef7",
    },
    "light": {
        "bg":         "#f3f6fd",
        "sidebar":    "#ffffff",
        "card":       "#ffffff",
        "card2":      "#f0f4ff",
        "border":     "#dce3f5",
        "accent":     "#2563eb",
        "accent_hv":  "#1d4ed8",
        "spam":       "#dc2626",
        "ham":        "#16a34a",
        "warn":       "#d97706",
        "text":       "#0f172a",
        "subtext":    "#64748b",
        "divider":    "#dce3f5",
        "btn_sec":    "#e8edf8",
        "btn_sec_hv": "#d5dcf0",
        "nav_active": "#2563eb",
        "nav_idle":   "#e8edf8",
        "footer":     "#e2e8f0",
        "donut_bg":   "#dce3f5",
        "loader":     "#2563eb",
    },
}

MODEL_FILES = [
    'models/vectorizer.pkl', 'models/naive_bayes.pkl',
    'models/svm.pkl',        'models/neural_network.pkl',
]
PLACEHOLDER = 'Paste or type the email content here...'


# ── Helpers ───────────────────────────────────────────────────────────────
def models_exist():
    return all(os.path.exists(p) for p in MODEL_FILES)


# ── Donut Chart ────────────────────────────────────────────────────────────
class DonutChart(Canvas):
    SIZE   = 170
    STROKE = 26

    def __init__(self, parent, bg_color, **kw):
        super().__init__(parent, width=self.SIZE, height=self.SIZE,
                         bg=bg_color, highlightthickness=0, **kw)
        self._bg_color    = bg_color
        self._ham_pct     = 0.0
        self._spam_pct    = 0.0
        self._ham_color   = "#3ecf8e"
        self._spam_color  = "#f05454"
        self._track_color = "#2d3a58"
        self._label_text  = ""
        self._sub_text    = ""
        self._visible     = False
        self._draw()

    def update_colors(self, bg, track, ham_c, spam_c):
        self._bg_color    = bg
        self._track_color = track
        self._ham_color   = ham_c
        self._spam_color  = spam_c
        self.configure(bg=bg)
        self._draw()

    def set_values(self, ham_pct, spam_pct, label="", sub="", visible=True):
        self._ham_pct    = ham_pct
        self._spam_pct   = spam_pct
        self._label_text = label
        self._sub_text   = sub
        self._visible    = visible
        self._draw()

    def _draw(self):
        self.delete('all')
        if not self._visible:
            return
        s   = self.SIZE
        pad = self.STROKE + 6
        x0, y0, x1, y1 = pad, pad, s - pad, s - pad

        # Track
        self.create_arc(x0, y0, x1, y1, start=0, extent=359.99,
                        outline=self._track_color, width=self.STROKE, style='arc')

        total = self._ham_pct + self._spam_pct
        if total > 0:
            ham_ext  = (self._ham_pct  / total) * 359.99
            spam_ext = (self._spam_pct / total) * 359.99
            self.create_arc(x0, y0, x1, y1, start=90, extent=ham_ext,
                            outline=self._ham_color, width=self.STROKE, style='arc')
            self.create_arc(x0, y0, x1, y1, start=90 + ham_ext, extent=spam_ext,
                            outline=self._spam_color, width=self.STROKE, style='arc')

        cx, cy = s // 2, s // 2
        is_spam = 'SPAM' in self._label_text.upper()
        fill = self._spam_color if is_spam else self._ham_color
        self.create_text(cx, cy - 10, text=self._label_text,
                         font=('Segoe UI', 13, 'bold'), fill=fill)
        self.create_text(cx, cy + 11, text=self._sub_text,
                         font=('Segoe UI', 9), fill='#7d8590')


# ── Loader Spinner ─────────────────────────────────────────────────────────
class LoaderSpinner(Canvas):
    SIZE = 28

    def __init__(self, parent, bg_color, color, **kw):
        super().__init__(parent, width=self.SIZE, height=self.SIZE,
                         bg=bg_color, highlightthickness=0, **kw)
        self._color   = color
        self._bg      = bg_color
        self._angle   = 0
        self._running = False
        self._job     = None

    def start(self):
        self._running = True
        self._spin()

    def stop(self):
        self._running = False
        if self._job:
            self.after_cancel(self._job)
            self._job = None
        self.delete('all')

    def update_colors(self, bg, color):
        self._bg    = bg
        self._color = color
        self.configure(bg=bg)

    def _spin(self):
        if not self._running:
            return
        self.delete('all')
        p = 3
        s = self.SIZE
        self.create_arc(p, p, s - p, s - p,
                        start=self._angle, extent=270,
                        outline=self._color, width=3, style='arc')
        self._angle = (self._angle + 14) % 360
        self._job   = self.after(28, self._spin)


# ── Sample Card ───────────────────────────────────────────────────────────
class SampleCard(ctk.CTkFrame):
    """Clickable card with colored SPAM/HAM badge."""

    def __init__(self, parent, tag: str, body: str, on_click, get_theme, **kw):
        C = get_theme()
        super().__init__(parent, fg_color=C["card"], corner_radius=8,
                         border_width=1, border_color=C["border"], **kw)
        self._body      = body
        self._on_click  = on_click
        self._get_theme = get_theme
        self._tag       = tag  # "SPAM" or "HAM"
        self.grid_columnconfigure(1, weight=1)

        # Colored pill badge
        badge_color = C["spam"] if tag == "SPAM" else C["ham"]
        self._badge = ctk.CTkLabel(
            self, text=f" {tag} ",
            font=ctk.CTkFont(family='Consolas', size=9, weight='bold'),
            text_color="#ffffff",
            fg_color=badge_color,
            corner_radius=4, width=42, height=18
        )
        self._badge.grid(row=0, column=0, padx=(10, 6), pady=(8, 2), sticky='w')

        short = body[:82] + "\u2026" if len(body) > 82 else body
        self._body_lbl = ctk.CTkLabel(
            self, text=short,
            font=ctk.CTkFont(family='Segoe UI', size=10),
            text_color=C["subtext"], anchor='w',
            justify='left', wraplength=200
        )
        self._body_lbl.grid(row=0, column=1, padx=(0, 10), pady=(6, 6), sticky='ew')

        for w in (self, self._badge, self._body_lbl):
            w.bind("<Button-1>", lambda e: self._on_click(self._body))
            w.bind("<Enter>",    lambda e: self._hover(True))
            w.bind("<Leave>",    lambda e: self._hover(False))

    def _hover(self, entering):
        C = self._get_theme()
        self.configure(fg_color=C["card2"] if entering else C["card"])

    def repaint(self):
        C = self._get_theme()
        self.configure(fg_color=C["card"], border_color=C["border"])
        badge_color = C["spam"] if self._tag == "SPAM" else C["ham"]
        self._badge.configure(fg_color=badge_color)
        self._body_lbl.configure(text_color=C["subtext"])


# ── Main Application ──────────────────────────────────────────────────────
class SpamDetectorApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self._mode         = "dark"
        self._is_animating = False
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(f"Spam Email Detector  {APP_VERSION}")
        self.geometry("1180x760")
        self.minsize(1000, 660)
        self.resizable(True, True)

        self._selected_model = ctk.StringVar(value='svm')
        self._current_view   = "analysis"
        self._sample_cards   = []

        self._build_ui()

    # ── Theme helpers ────────────────────────────────────────────────────
    @property
    def C(self):
        return THEME[self._mode]

    def _toggle_theme(self):
        if self._is_animating:
            return
        self._is_animating = True
        self._mode = "light" if self._mode == "dark" else "dark"
        ctk.set_appearance_mode(self._mode)
        self._theme_btn.configure(
            text="\u2600\ufe0f  Light Mode" if self._mode == "light" else "\U0001f319  Dark Mode"
        )
        self._repaint()
        self._is_animating = False

    def _repaint(self):
        C = self.C
        self.configure(fg_color=C["bg"])
        # sidebar
        self._sidebar.configure(fg_color=C["sidebar"])
        for d in self._dividers:
            d.configure(fg_color=C["divider"])
        self._logo_icon.configure(text_color=C["accent"])
        self._logo_lbl.configure(text_color=C["accent"])
        self._app_sub_lbl.configure(text_color=C["subtext"])
        self._nav_lbl.configure(text_color=C["subtext"])
        self._model_lbl.configure(text_color=C["subtext"])
        self._theme_btn.configure(fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"], text_color=C["text"])
        self._train_btn.configure(fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"], text_color=C["text"])
        self._version_lbl.configure(text_color=C["subtext"])
        for rb in self._radio_buttons:
            rb.configure(text_color=C["text"], fg_color=C["accent"], border_color=C["border"])
        # nav
        self._btn_analysis.configure(
            fg_color=C["nav_active"] if self._current_view == "analysis" else C["nav_idle"],
            text_color="#ffffff" if self._current_view == "analysis" else C["text"],
            hover_color=C["accent_hv"])
        self._btn_reports.configure(
            fg_color=C["nav_active"] if self._current_view == "reports" else C["nav_idle"],
            text_color="#ffffff" if self._current_view == "reports" else C["text"],
            hover_color=C["accent_hv"])
        # header
        self._header_frame.configure(fg_color=C["sidebar"])
        self._header_label.configure(text_color=C["text"])
        # main
        self._main_frame.configure(fg_color=C["bg"])
        self._status_label.configure(text_color=C["subtext"])
        # footer
        self._footer_frame.configure(fg_color=C["footer"])
        self._footer_lbl.configure(text_color=C["subtext"], fg_color=C["footer"])
        # analysis view
        self._content_frame.configure(fg_color=C["bg"])
        self._left_panel.configure(fg_color=C["bg"])
        self._right_panel.configure(fg_color=C["bg"])
        self._email_lbl.configure(text_color=C["text"])
        self._samples_lbl.configure(text_color=C["text"])
        self._text_input.configure(fg_color=C["card"], border_color=C["border"])
        self._analyze_btn.configure(fg_color=C["accent"], hover_color=C["accent_hv"])
        self._clear_btn.configure(fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"], text_color=C["text"])
        self._result_card.configure(fg_color=C["card"], border_color=C["border"])
        self._verdict_label.configure(text_color=C["subtext"])
        self._model_info_label.configure(text_color=C["subtext"])
        # sample cards
        for card in self._sample_cards:
            card.repaint()
        # donut
        self._donut.update_colors(bg=C["card"], track=C["donut_bg"],
                                   ham_c=C["ham"], spam_c=C["spam"])
        # spinners
        self._analyze_spinner.update_colors(bg=C["bg"], color=C["loader"])
        self._train_spinner.update_colors(bg=C["btn_sec"], color=C["loader"])
        # reports
        self._reports_frame.configure(fg_color=C["bg"])
        self._scroll_frame.configure(fg_color=C["bg"])
        self._metrics_frame.configure(fg_color=C["card"], border_color=C["border"])
        for lbl in self._metric_header_lbls:
            lbl.configure(text_color=C["accent"])
        for lbl in self._metric_model_lbls:
            lbl.configure(text_color=C["text"])
        for row in self._metric_rows:
            for lbl in row:
                lbl.configure(text_color=C["subtext"])
        self._refresh_btn.configure(fg_color=C["accent"], hover_color=C["accent_hv"])
        # fix spinner bg for reports (inside scrollable)
        self._reports_spinner.update_colors(bg=C["bg"], color=C["loader"])
        self._cm_title_lbl.configure(text_color=C["text"])
        for lbl in self._cm_labels:
            lbl.configure(text_color=C["subtext"])

    # ── Build UI ───────────────────────────────────────────────────────
    def _build_ui(self):
        self.configure(fg_color=self.C["bg"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

    # ── Sidebar ───────────────────────────────────────────────────────
    def _build_sidebar(self):
        C = self.C
        self._sidebar = ctk.CTkFrame(
            self, width=258, corner_radius=0,
            fg_color=C["sidebar"], border_width=1, border_color=C["border"]
        )
        self._sidebar.grid(row=0, column=0, sticky='nsew')
        self._sidebar.grid_propagate(False)
        self._sidebar.grid_columnconfigure(0, weight=1)
        # FIX: explicit row heights — no weight on middle rows to prevent compression
        self._dividers = []

        row = 0

        # Logo row
        logo_row = ctk.CTkFrame(self._sidebar, fg_color='transparent')
        logo_row.grid(row=row, column=0, padx=18, pady=(24, 2), sticky='w'); row += 1

        self._logo_icon = ctk.CTkLabel(
            logo_row, text="\u2709",
            font=ctk.CTkFont(size=24), text_color=C["accent"]
        )
        self._logo_icon.grid(row=0, column=0, padx=(0, 8))

        self._logo_lbl = ctk.CTkLabel(
            logo_row, text="SPAM DETECTOR",
            font=ctk.CTkFont(family='Consolas', size=13, weight='bold'),
            text_color=C["accent"]
        )
        self._logo_lbl.grid(row=0, column=1)

        self._app_sub_lbl = ctk.CTkLabel(
            self._sidebar, text="NLP & Machine Learning",
            font=ctk.CTkFont(family='Segoe UI', size=10),
            text_color=C["subtext"]
        )
        self._app_sub_lbl.grid(row=row, column=0, padx=20, pady=(0, 14), sticky='w'); row += 1

        d = ctk.CTkFrame(self._sidebar, height=1, fg_color=C["divider"])
        d.grid(row=row, column=0, padx=14, sticky='ew'); self._dividers.append(d); row += 1

        # Nav label
        self._nav_lbl = ctk.CTkLabel(
            self._sidebar, text="NAVIGATION",
            font=ctk.CTkFont(family='Segoe UI', size=9, weight='bold'),
            text_color=C["subtext"]
        )
        self._nav_lbl.grid(row=row, column=0, padx=20, pady=(12, 4), sticky='w'); row += 1

        self._btn_analysis = ctk.CTkButton(
            self._sidebar, text="\u2709  Email Analysis",
            command=lambda: self._switch_view('analysis'),
            height=36, corner_radius=8, anchor='w',
            fg_color=C["nav_active"], hover_color=C["accent_hv"],
            text_color="#ffffff",
            font=ctk.CTkFont(family='Segoe UI', size=12, weight='bold')
        )
        self._btn_analysis.grid(row=row, column=0, padx=12, pady=2, sticky='ew'); row += 1

        self._btn_reports = ctk.CTkButton(
            self._sidebar, text="\U0001f4ca  Model Reports",
            command=lambda: self._switch_view('reports'),
            height=36, corner_radius=8, anchor='w',
            fg_color=C["nav_idle"], hover_color=C["accent_hv"],
            text_color=C["text"],
            font=ctk.CTkFont(family='Segoe UI', size=12)
        )
        self._btn_reports.grid(row=row, column=0, padx=12, pady=2, sticky='ew'); row += 1

        d = ctk.CTkFrame(self._sidebar, height=1, fg_color=C["divider"])
        d.grid(row=row, column=0, padx=14, pady=(12, 0), sticky='ew'); self._dividers.append(d); row += 1

        # Model selector
        self._model_lbl = ctk.CTkLabel(
            self._sidebar, text="SELECT MODEL",
            font=ctk.CTkFont(family='Segoe UI', size=9, weight='bold'),
            text_color=C["subtext"]
        )
        self._model_lbl.grid(row=row, column=0, padx=20, pady=(12, 4), sticky='w'); row += 1

        self._radio_buttons = []
        for label, value in [
            ("Naive Bayes",            "naive_bayes"),
            ("Support Vector Machine", "svm"),
            ("Neural Network",         "neural_network"),
        ]:
            rb = ctk.CTkRadioButton(
                self._sidebar, text=f"  {label}",
                variable=self._selected_model, value=value,
                font=ctk.CTkFont(family='Segoe UI', size=12),
                text_color=C["text"], fg_color=C["accent"],
                border_color=C["border"]
            )
            rb.grid(row=row, column=0, padx=24, pady=3, sticky='w'); row += 1
            self._radio_buttons.append(rb)

        d = ctk.CTkFrame(self._sidebar, height=1, fg_color=C["divider"])
        d.grid(row=row, column=0, padx=14, pady=(12, 0), sticky='ew'); self._dividers.append(d); row += 1

        # Theme toggle
        self._theme_btn = ctk.CTkButton(
            self._sidebar, text="\U0001f319  Dark Mode",
            command=self._toggle_theme, height=34,
            fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"],
            text_color=C["text"],
            font=ctk.CTkFont(family='Segoe UI', size=11), corner_radius=8
        )
        self._theme_btn.grid(row=row, column=0, padx=12, pady=(10, 4), sticky='ew'); row += 1

        # Train + spinner
        train_row = ctk.CTkFrame(self._sidebar, fg_color='transparent')
        train_row.grid(row=row, column=0, padx=12, pady=4, sticky='ew')
        train_row.grid_columnconfigure(0, weight=1); row += 1

        self._train_btn = ctk.CTkButton(
            train_row, text="\u26a1  Train Models",
            command=self._train_models, height=34,
            fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"],
            text_color=C["text"],
            font=ctk.CTkFont(family='Segoe UI', size=11), corner_radius=8
        )
        self._train_btn.grid(row=0, column=0, sticky='ew')

        self._train_spinner = LoaderSpinner(
            train_row, bg_color=C["btn_sec"], color=C["loader"]
        )
        self._train_spinner.grid(row=0, column=1, padx=(6, 0))

        d = ctk.CTkFrame(self._sidebar, height=1, fg_color=C["divider"])
        d.grid(row=row, column=0, padx=14, pady=(10, 0), sticky='ew'); self._dividers.append(d); row += 1

        self._version_lbl = ctk.CTkLabel(
            self._sidebar, text=APP_VERSION,
            font=ctk.CTkFont(family='Consolas', size=9),
            text_color=C["subtext"]
        )
        self._version_lbl.grid(row=row, column=0, padx=20, pady=(8, 16), sticky='w')

    # ── Main ────────────────────────────────────────────────────────────
    def _build_main(self):
        C = self.C
        self._main_frame = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        self._main_frame.grid(row=0, column=1, sticky='nsew')
        self._main_frame.grid_rowconfigure(1, weight=1)
        self._main_frame.grid_columnconfigure(0, weight=1)

        # Header
        self._header_frame = ctk.CTkFrame(
            self._main_frame, fg_color=C["sidebar"], height=56, corner_radius=0
        )
        self._header_frame.grid(row=0, column=0, sticky='ew')
        self._header_frame.grid_propagate(False)
        self._header_frame.grid_columnconfigure(0, weight=1)

        self._header_label = ctk.CTkLabel(
            self._header_frame, text="\u2709  Email Analysis",
            font=ctk.CTkFont(family='Segoe UI', size=14, weight='bold'),
            text_color=C["text"]
        )
        self._header_label.grid(row=0, column=0, padx=26, pady=14, sticky='w')

        self._view_analysis = self._build_analysis_view(self._main_frame)
        self._view_reports  = self._build_reports_view(self._main_frame)

        # Status bar
        self._status_label = ctk.CTkLabel(
            self._main_frame, text="\u2022  Ready",
            font=ctk.CTkFont(family='Consolas', size=10),
            text_color=C["subtext"]
        )
        self._status_label.grid(row=2, column=0, padx=26, pady=(2, 0), sticky='w')

        # Footer
        self._footer_frame = ctk.CTkFrame(
            self._main_frame, fg_color=C["footer"], height=30, corner_radius=0
        )
        self._footer_frame.grid(row=3, column=0, sticky='ew')
        self._footer_frame.grid_propagate(False)

        team_str = "  \u00b7  ".join(TEAM_MEMBERS)
        self._footer_lbl = ctk.CTkLabel(
            self._footer_frame,
            text=f"\U0001f393  {team_str}  \u00b7  {APP_VERSION}",
            font=ctk.CTkFont(family='Segoe UI', size=10),
            text_color=C["subtext"], fg_color=C["footer"]
        )
        self._footer_lbl.place(relx=0.5, rely=0.5, anchor='center')

        self._switch_view('analysis')

    # ── Analysis View ─────────────────────────────────────────────────
    def _build_analysis_view(self, parent):
        C = self.C
        frame = ctk.CTkFrame(parent, fg_color=C["bg"])
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self._content_frame = ctk.CTkFrame(frame, fg_color=C["bg"])
        self._content_frame.grid(row=0, column=0, sticky='nsew', padx=22, pady=16)
        self._content_frame.grid_rowconfigure(0, weight=1)
        self._content_frame.grid_columnconfigure(0, weight=3)
        self._content_frame.grid_columnconfigure(1, weight=2)

        # Left panel
        self._left_panel = ctk.CTkFrame(self._content_frame, fg_color=C["bg"])
        self._left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        self._left_panel.grid_rowconfigure(1, weight=1)
        self._left_panel.grid_columnconfigure(0, weight=1)

        self._email_lbl = ctk.CTkLabel(
            self._left_panel, text="\u2709  Email Content",
            font=ctk.CTkFont(family='Segoe UI', size=12, weight='bold'),
            text_color=C["text"]
        )
        self._email_lbl.grid(row=0, column=0, sticky='w', pady=(0, 6))

        self._text_input = ctk.CTkTextbox(
            self._left_panel, corner_radius=10,
            fg_color=C["card"], border_color=C["border"], border_width=1,
            text_color=C["subtext"],
            font=ctk.CTkFont(family='Segoe UI', size=13), wrap='word'
        )
        self._text_input.grid(row=1, column=0, sticky='nsew')
        self._text_input.insert('0.0', PLACEHOLDER)
        self._text_input.bind('<FocusIn>',  self._clear_placeholder)
        self._text_input.bind('<FocusOut>', self._restore_placeholder)

        # Buttons
        btn_row = ctk.CTkFrame(self._left_panel, fg_color='transparent')
        btn_row.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        btn_row.grid_columnconfigure(0, weight=1)

        self._analyze_btn = ctk.CTkButton(
            btn_row, text="\U0001f50d  Analyze",
            command=self._analyze, height=42,
            font=ctk.CTkFont(family='Segoe UI', size=13, weight='bold'),
            fg_color=C["accent"], hover_color=C["accent_hv"], corner_radius=10
        )
        self._analyze_btn.grid(row=0, column=0, sticky='ew')

        self._analyze_spinner = LoaderSpinner(btn_row, bg_color=C["bg"], color=C["loader"])
        self._analyze_spinner.grid(row=0, column=1, padx=(8, 0))

        self._clear_btn = ctk.CTkButton(
            btn_row, text="\u2715  Clear",
            command=self._clear_all, height=42,
            font=ctk.CTkFont(family='Segoe UI', size=12),
            fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"],
            text_color=C["text"], corner_radius=10, width=100
        )
        self._clear_btn.grid(row=0, column=2, padx=(8, 0))

        # Result card
        self._result_card = ctk.CTkFrame(
            self._left_panel, fg_color=C["card"],
            corner_radius=12, border_width=1, border_color=C["border"]
        )
        self._result_card.grid(row=3, column=0, sticky='ew', pady=(12, 0))
        self._result_card.grid_columnconfigure(0, weight=1)

        verdict_col = ctk.CTkFrame(self._result_card, fg_color='transparent')
        verdict_col.grid(row=0, column=0, sticky='w', padx=18, pady=14)

        self._verdict_label = ctk.CTkLabel(
            verdict_col, text="Awaiting Analysis",
            font=ctk.CTkFont(family='Segoe UI', size=15, weight='bold'),
            text_color=C["subtext"]
        )
        self._verdict_label.grid(row=0, column=0, sticky='w')

        self._model_info_label = ctk.CTkLabel(
            verdict_col, text="",
            font=ctk.CTkFont(family='Segoe UI', size=10),
            text_color=C["subtext"]
        )
        self._model_info_label.grid(row=1, column=0, sticky='w', pady=(3, 0))

        # Donut — hidden until first result
        self._donut = DonutChart(self._result_card, bg_color=C["card"])
        self._donut.grid(row=0, column=1, padx=(0, 14), pady=10)
        self._donut.set_values(0, 0, visible=False)

        # Right panel — sample emails
        self._right_panel = ctk.CTkFrame(self._content_frame, fg_color=C["bg"])
        self._right_panel.grid(row=0, column=1, sticky='nsew')
        self._right_panel.grid_rowconfigure(1, weight=1)
        self._right_panel.grid_columnconfigure(0, weight=1)

        self._samples_lbl = ctk.CTkLabel(
            self._right_panel, text="\U0001f4e8  Sample Emails",
            font=ctk.CTkFont(family='Segoe UI', size=12, weight='bold'),
            text_color=C["text"]
        )
        self._samples_lbl.grid(row=0, column=0, sticky='w', pady=(0, 6))

        samples_scroll = ctk.CTkScrollableFrame(
            self._right_panel, fg_color=C["bg"], corner_radius=0
        )
        samples_scroll.grid(row=1, column=0, sticky='nsew')
        samples_scroll.grid_columnconfigure(0, weight=1)

        self._sample_cards = []
        for idx, (tag, body) in enumerate(SAMPLE_EMAILS):
            card = SampleCard(
                samples_scroll,
                tag=tag, body=body,
                on_click=self._load_sample,
                get_theme=lambda: self.C
            )
            card.grid(row=idx, column=0, sticky='ew', pady=3, padx=2)
            self._sample_cards.append(card)

        return frame

    # ── Reports View ─────────────────────────────────────────────────
    def _build_reports_view(self, parent):
        C = self.C
        self._reports_frame = ctk.CTkFrame(parent, fg_color=C["bg"])
        self._reports_frame.grid_rowconfigure(0, weight=1)
        self._reports_frame.grid_columnconfigure(0, weight=1)

        self._scroll_frame = ctk.CTkScrollableFrame(self._reports_frame, fg_color=C["bg"])
        self._scroll_frame.grid(row=0, column=0, sticky='nsew', padx=26, pady=18)
        self._scroll_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self._scroll_frame,
            text="\U0001f4ca  Model Performance Reports",
            font=ctk.CTkFont(family='Segoe UI', size=15, weight='bold'),
            text_color=C["text"]
        ).grid(row=0, column=0, sticky='w', pady=(0, 3))

        ctk.CTkLabel(
            self._scroll_frame,
            text="Evaluation of all trained classifiers on the SMS Spam Collection dataset.",
            font=ctk.CTkFont(family='Segoe UI', size=11),
            text_color=C["subtext"]
        ).grid(row=1, column=0, sticky='w', pady=(0, 12))

        # Metrics table
        self._metrics_frame = ctk.CTkFrame(
            self._scroll_frame, fg_color=C["card"],
            corner_radius=10, border_width=1, border_color=C["border"]
        )
        self._metrics_frame.grid(row=2, column=0, sticky='ew', pady=(0, 12))
        self._metrics_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self._metric_header_lbls = []
        for col, h in enumerate(['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score']):
            lbl = ctk.CTkLabel(
                self._metrics_frame, text=h,
                font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
                text_color=C["accent"]
            )
            lbl.grid(row=0, column=col, padx=14, pady=10, sticky='w')
            self._metric_header_lbls.append(lbl)

        ctk.CTkFrame(self._metrics_frame, height=1, fg_color=C["divider"]).grid(
            row=1, column=0, columnspan=5, sticky='ew', padx=8)

        self._metric_rows       = []
        self._metric_model_lbls = []
        for r_idx, name in enumerate(['Naive Bayes', 'Support Vector Machine', 'Neural Network']):
            ml = ctk.CTkLabel(
                self._metrics_frame, text=name,
                font=ctk.CTkFont(family='Segoe UI', size=12),
                text_color=C["text"]
            )
            ml.grid(row=r_idx + 2, column=0, padx=14, pady=9, sticky='w')
            self._metric_model_lbls.append(ml)
            row_lbls = []
            for col in range(1, 5):
                lbl = ctk.CTkLabel(
                    self._metrics_frame, text="--",
                    font=ctk.CTkFont(family='Consolas', size=12),
                    text_color=C["subtext"]
                )
                lbl.grid(row=r_idx + 2, column=col, padx=14, pady=9, sticky='w')
                row_lbls.append(lbl)
            self._metric_rows.append(row_lbls)

        # Refresh row
        ref_row = ctk.CTkFrame(self._scroll_frame, fg_color='transparent')
        ref_row.grid(row=3, column=0, sticky='w', pady=(0, 20))

        self._refresh_btn = ctk.CTkButton(
            ref_row, text="\u27f3  Load / Refresh Results",
            command=self._load_reports, height=36,
            fg_color=C["accent"], hover_color=C["accent_hv"],
            corner_radius=8, font=ctk.CTkFont(family='Segoe UI', size=12)
        )
        self._refresh_btn.grid(row=0, column=0)

        # FIX: use bg=C["bg"] not C["sidebar"] for spinner inside scrollable
        self._reports_spinner = LoaderSpinner(
            ref_row, bg_color=C["bg"], color=C["loader"]
        )
        self._reports_spinner.grid(row=0, column=1, padx=(10, 0))

        self._cm_title_lbl = ctk.CTkLabel(
            self._scroll_frame, text="\U0001f5bc  Confusion Matrices",
            font=ctk.CTkFont(family='Segoe UI', size=13, weight='bold'),
            text_color=C["text"]
        )
        self._cm_title_lbl.grid(row=4, column=0, sticky='w', pady=(0, 10))

        cm_grid = ctk.CTkFrame(self._scroll_frame, fg_color='transparent')
        cm_grid.grid(row=5, column=0, sticky='ew')
        cm_grid.grid_columnconfigure((0, 1, 2), weight=1)

        self._cm_labels = []
        for col, title in enumerate(['Naive Bayes', 'SVM', 'Neural Network']):
            ctk.CTkLabel(
                cm_grid, text=title,
                font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
                text_color=C["subtext"]
            ).grid(row=0, column=col, pady=(0, 5))
            lbl = ctk.CTkLabel(
                cm_grid, text="[ Run training to generate ]",
                text_color=C["subtext"],
                font=ctk.CTkFont(family='Segoe UI', size=10)
            )
            lbl.grid(row=1, column=col, padx=6)
            self._cm_labels.append(lbl)

        return self._reports_frame

    # ── View Switching ─────────────────────────────────────────────────
    def _switch_view(self, view: str):
        C = self.C
        self._view_analysis.grid_forget()
        self._view_reports.grid_forget()
        if view == 'analysis':
            self._view_analysis.grid(row=1, column=0, sticky='nsew')
            self._header_label.configure(text="\u2709  Email Analysis")
            self._btn_analysis.configure(fg_color=C["nav_active"], text_color="#ffffff",
                                          font=ctk.CTkFont(family='Segoe UI', size=12, weight='bold'))
            self._btn_reports.configure(fg_color=C["nav_idle"], text_color=C["text"],
                                         font=ctk.CTkFont(family='Segoe UI', size=12))
        else:
            self._view_reports.grid(row=1, column=0, sticky='nsew')
            self._header_label.configure(text="\U0001f4ca  Model Performance Reports")
            self._btn_reports.configure(fg_color=C["nav_active"], text_color="#ffffff",
                                         font=ctk.CTkFont(family='Segoe UI', size=12, weight='bold'))
            self._btn_analysis.configure(fg_color=C["nav_idle"], text_color=C["text"],
                                          font=ctk.CTkFont(family='Segoe UI', size=12))
            self._load_reports()
        self._current_view = view

    # ── Sample load ────────────────────────────────────────────────────
    def _load_sample(self, body: str):
        self._text_input.delete('0.0', 'end')
        self._text_input.insert('0.0', body)
        self._text_input.configure(text_color=self.C["text"])
        self._set_status("\u2022  Sample loaded — click Analyze")

    # ── Reports logic ────────────────────────────────────────────────
    def _load_reports(self):
        if not models_exist():
            self._set_status("\u26a0  Models not found — train first")
            return
        self._set_status("\u23f3  Loading reports...")
        self._reports_spinner.start()
        threading.Thread(target=self._compute_reports, daemon=True).start()

    def _compute_reports(self):
        try:
            from src.preprocess import load_and_preprocess
            from src.predict    import load_model
            from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
            X_train, X_test, y_train, y_test, _ = load_and_preprocess()
            results = []
            for key in ['naive_bayes', 'svm', 'neural_network']:
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
            self.after(0, self._reports_spinner.stop)
            self.after(0, self._set_status, "\u2714  Reports loaded")
        except Exception as e:
            self.after(0, self._reports_spinner.stop)
            self.after(0, self._set_status, f"\u26a0  {e}")

    def _update_metrics_table(self, results):
        C = self.C
        for row_labels, m in zip(self._metric_rows, results):
            for lbl, val in zip(row_labels, [
                f"{m['accuracy']*100:.2f}%",
                f"{m['precision']*100:.2f}%",
                f"{m['recall']*100:.2f}%",
                f"{m['f1']*100:.2f}%",
            ]):
                lbl.configure(text=val, text_color=C["text"])

    def _load_cm_images(self):
        try:
            from PIL import Image as PILImage
            for lbl, fpath in zip(self._cm_labels, [
                'reports/cm_naive_bayes.png',
                'reports/cm_svm.png',
                'reports/cm_neural_network.png',
            ]):
                if os.path.exists(fpath):
                    img   = PILImage.open(fpath).resize((290, 240))
                    ctk_i = ctk.CTkImage(light_image=img, dark_image=img, size=(290, 240))
                    lbl.configure(image=ctk_i, text="")
                    lbl._ctk_image = ctk_i
        except ImportError:
            self._set_status("\u26a0  pip install Pillow")

    # ── Analysis logic ────────────────────────────────────────────────
    def _analyze(self):
        text = self._text_input.get('0.0', 'end').strip()
        if not text or text == PLACEHOLDER:
            messagebox.showwarning("Input Required", "Please enter email content.")
            return
        if not models_exist():
            messagebox.showerror("Models Not Found",
                                 "No trained models found.\nClick \u26a1 Train Models first.")
            return
        self._set_status("\u23f3  Analyzing...")
        self._analyze_spinner.start()
        self._verdict_label.configure(text="Analyzing...",
                                       text_color=self.C["subtext"],
                                       font=ctk.CTkFont(family='Segoe UI', size=14))
        self._model_info_label.configure(text="")
        self._donut.set_values(0, 0, visible=False)
        threading.Thread(target=self._run_prediction,
                         args=(text,), daemon=True).start()

    def _run_prediction(self, text):
        try:
            from src.predict import predict
            result = predict(text, model_name=self._selected_model.get())
            self.after(0, self._show_result, result)
        except Exception as e:
            self.after(0, self._analyze_spinner.stop)
            self.after(0, self._show_error, str(e))

    def _show_result(self, result):
        C = self.C
        self._analyze_spinner.stop()
        label      = result['label']
        confidence = result['confidence']
        spam_prob  = result['spam_prob']
        ham_prob   = result['ham_prob']
        model_name = self._selected_model.get().replace('_', ' ').title()
        color = C["spam"] if label == 'Spam' else C["ham"]
        icon  = "\U0001f6ab" if label == 'Spam' else "\u2705"

        self._verdict_label.configure(
            text=f"{icon}  {label.upper()}  —  {confidence}% Confidence",
            font=ctk.CTkFont(family='Segoe UI', size=15, weight='bold'),
            text_color=color
        )
        self._model_info_label.configure(
            text=f"Model: {model_name}   Ham: {ham_prob}%   Spam: {spam_prob}%"
        )
        self._donut.set_values(
            ham_pct=ham_prob, spam_pct=spam_prob,
            label=f"{label}\n{confidence}%",
            sub="confidence",
            visible=True
        )
        self._set_status(f"\u2714  Done  |  Ham {ham_prob}%  |  Spam {spam_prob}%")

    def _show_error(self, error):
        messagebox.showerror("Prediction Error", f"Prediction failed:\n{error}")
        self._set_status("\u26a0  Error occurred.")
        self._verdict_label.configure(text="Analysis failed.", text_color=self.C["spam"])

    def _train_models(self):
        self._set_status("\u23f3  Training... please wait.")
        self._train_spinner.start()
        threading.Thread(target=self._run_training, daemon=True).start()

    def _run_training(self):
        try:
            from src.train import train_all
            train_all()
            self.after(0, self._train_spinner.stop)
            self.after(0, self._set_status, "\u2714  All 3 models trained successfully.")
            self.after(0, messagebox.showinfo, "Done", "All 3 models trained and saved.")
        except Exception as e:
            self.after(0, self._train_spinner.stop)
            self.after(0, messagebox.showerror, "Training Error", str(e))
            self.after(0, self._set_status, "\u26a0  Training failed.")

    # ── Utils ──────────────────────────────────────────────────────────
    def _clear_all(self):
        self._text_input.delete('0.0', 'end')
        self._text_input.insert('0.0', PLACEHOLDER)
        self._text_input.configure(text_color=self.C["subtext"])
        self._verdict_label.configure(
            text="Awaiting Analysis",
            font=ctk.CTkFont(family='Segoe UI', size=15, weight='bold'),
            text_color=self.C["subtext"]
        )
        self._model_info_label.configure(text="")
        self._donut.set_values(0, 0, visible=False)
        self._set_status("\u2022  Ready")

    def _clear_placeholder(self, event):
        if self._text_input.get('0.0', 'end').strip() == PLACEHOLDER:
            self._text_input.delete('0.0', 'end')
            self._text_input.configure(text_color=self.C["text"])

    def _restore_placeholder(self, event):
        if not self._text_input.get('0.0', 'end').strip():
            self._text_input.insert('0.0', PLACEHOLDER)
            self._text_input.configure(text_color=self.C["subtext"])

    def _set_status(self, message):
        self._status_label.configure(text=message)


# ── Entry point ───────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = SpamDetectorApp()
    app.mainloop()
