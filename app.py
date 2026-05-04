"""
Spam Email Detector  v1.4.1
Full redesign: icons, donut chart, theme transition,
footer, sample emails, loader spinner, custom fonts.
Fix: wraplength removed — sample cards use CTkFrame+Label.
"""
import customtkinter as ctk
from tkinter import messagebox, Canvas
import threading
import os, sys, math, time

# ── Version ──────────────────────────────────────────────────────────────
APP_TITLE   = "Spam Email Detector"
APP_VERSION = "v1.4.1"

TEAM_MEMBERS = [
    "Ahmed Hussien",
    "Mohamed Ali",
    "Sara Khaled",
]

# ── Sample Emails ─────────────────────────────────────────────────────────
SAMPLE_EMAILS = [
    ("🔴 Spam", "Congratulations! You've been selected to receive a FREE iPhone 15. Click the link NOW to claim your prize before it expires!"),
    ("🔴 Spam", "URGENT: Your bank account has been compromised. Verify your details immediately at secure-bank-login.xyz or your account will be suspended."),
    ("🔴 Spam", "Win $1,000,000 cash! You are our lucky winner this week. Send your name and address to collect your reward. Limited time offer!"),
    ("🟢 Ham",  "Hey, are we still on for the meeting tomorrow at 10am? Let me know if you need to reschedule."),
    ("🟢 Ham",  "The project report has been uploaded to the shared drive. Please review section 3 and send your feedback by Friday."),
    ("🟢 Ham",  "Reminder: Your dentist appointment is confirmed for Thursday at 2:30 PM. Please arrive 10 minutes early."),
]

# ── Theme Palettes ────────────────────────────────────────────────────────
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
def resource_path(rel):
    base = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base, rel)

def models_exist():
    return all(os.path.exists(p) for p in MODEL_FILES)


# ── Donut Chart (Canvas) ──────────────────────────────────────────────────
class DonutChart(Canvas):
    """Pure-tkinter donut chart."""
    SIZE   = 180
    STROKE = 28

    def __init__(self, parent, bg_color, **kw):
        super().__init__(
            parent,
            width=self.SIZE, height=self.SIZE,
            bg=bg_color, highlightthickness=0,
            **kw
        )
        self._bg_color    = bg_color
        self._ham_pct     = 0.0
        self._spam_pct    = 0.0
        self._ham_color   = "#3ecf8e"
        self._spam_color  = "#f05454"
        self._track_color = "#2d3a58"
        self._label_text  = ""
        self._sub_text    = ""
        self._draw()

    def update_colors(self, bg, track, ham_c, spam_c):
        self._bg_color    = bg
        self._track_color = track
        self._ham_color   = ham_c
        self._spam_color  = spam_c
        self.configure(bg=bg)
        self._draw()

    def set_values(self, ham_pct: float, spam_pct: float, label="", sub=""):
        self._ham_pct    = ham_pct
        self._spam_pct   = spam_pct
        self._label_text = label
        self._sub_text   = sub
        self._draw()

    def _draw(self):
        self.delete('all')
        s   = self.SIZE
        pad = self.STROKE + 6
        x0, y0 = pad, pad
        x1, y1 = s - pad, s - pad

        self.create_arc(x0, y0, x1, y1,
                        start=0, extent=359.99,
                        outline=self._track_color,
                        width=self.STROKE, style='arc')

        total = self._ham_pct + self._spam_pct
        if total > 0:
            ham_ext  = (self._ham_pct  / total) * 359.99
            spam_ext = (self._spam_pct / total) * 359.99
            self.create_arc(x0, y0, x1, y1,
                            start=90, extent=ham_ext,
                            outline=self._ham_color,
                            width=self.STROKE, style='arc')
            self.create_arc(x0, y0, x1, y1,
                            start=90 + ham_ext, extent=spam_ext,
                            outline=self._spam_color,
                            width=self.STROKE, style='arc')

        cx, cy = s // 2, s // 2
        fill_main = (self._ham_color  if 'HAM'  in self._label_text.upper() else
                     self._spam_color if self._label_text else '#7d8590')
        self.create_text(cx, cy - 10,
                         text=self._label_text,
                         font=('Segoe UI', 15, 'bold'),
                         fill=fill_main)
        self.create_text(cx, cy + 12,
                         text=self._sub_text,
                         font=('Segoe UI', 9),
                         fill='#7d8590')


# ── Loader Spinner (Canvas) ───────────────────────────────────────────────
class LoaderSpinner(Canvas):
    SIZE = 32

    def __init__(self, parent, bg_color, color, **kw):
        super().__init__(parent, width=self.SIZE, height=self.SIZE,
                         bg=bg_color, highlightthickness=0, **kw)
        self._color    = color
        self._bg_color = bg_color
        self._angle    = 0
        self._running  = False
        self._job      = None

    def start(self):
        self._running = True
        self._spin()

    def stop(self):
        self._running = False
        if self._job:
            self.after_cancel(self._job)
        self.delete('all')

    def update_colors(self, bg, color):
        self._bg_color = bg
        self._color    = color
        self.configure(bg=bg)

    def _spin(self):
        if not self._running:
            return
        self.delete('all')
        s   = self.SIZE
        pad = 4
        self.create_arc(pad, pad, s - pad, s - pad,
                        start=self._angle, extent=270,
                        outline=self._color, width=3, style='arc')
        self._angle = (self._angle + 12) % 360
        self._job   = self.after(30, self._spin)


# ── Sample Email Card (clickable frame) ───────────────────────────────────
class SampleCard(ctk.CTkFrame):
    """A clickable card that replaces CTkButton to support text wrapping."""

    def __init__(self, parent, tag: str, body: str, on_click, theme_getter, **kw):
        C = theme_getter()
        super().__init__(
            parent,
            fg_color=C["card"], corner_radius=8,
            border_width=1, border_color=C["border"],
            **kw
        )
        self._body         = body
        self._on_click     = on_click
        self._theme_getter = theme_getter
        self.grid_columnconfigure(0, weight=1)

        self._tag_lbl = ctk.CTkLabel(
            self, text=tag,
            font=ctk.CTkFont(family='Segoe UI', size=10, weight='bold'),
            text_color=C["accent"], anchor='w'
        )
        self._tag_lbl.grid(row=0, column=0, sticky='w', padx=10, pady=(8, 2))

        short = body[:80] + "…" if len(body) > 80 else body
        self._body_lbl = ctk.CTkLabel(
            self, text=short,
            font=ctk.CTkFont(family='Segoe UI', size=10),
            text_color=C["subtext"], anchor='w',
            justify='left', wraplength=210
        )
        self._body_lbl.grid(row=1, column=0, sticky='w', padx=10, pady=(0, 8))

        # Bind click on all children
        for widget in (self, self._tag_lbl, self._body_lbl):
            widget.bind("<Button-1>",  lambda e: self._on_click(self._body))
            widget.bind("<Enter>",     lambda e: self._hover(True))
            widget.bind("<Leave>",     lambda e: self._hover(False))

    def _hover(self, entering: bool):
        C = self._theme_getter()
        self.configure(fg_color=C["card2"] if entering else C["card"])

    def repaint(self):
        C = self._theme_getter()
        self.configure(fg_color=C["card"], border_color=C["border"])
        self._tag_lbl.configure(text_color=C["accent"])
        self._body_lbl.configure(text_color=C["subtext"])


# ── Main Application ──────────────────────────────────────────────────────
class SpamDetectorApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self._mode         = "dark"
        self._is_animating = False
        ctk.set_appearance_mode(self._mode)
        ctk.set_default_color_theme("blue")

        self.title(f"\u26e3  {APP_TITLE}  {APP_VERSION}")
        self.geometry("1160x740")
        self.minsize(980, 640)
        self.resizable(True, True)

        self._selected_model = ctk.StringVar(value='svm')
        self._current_view   = "analysis"
        self._sample_cards   = []

        self._build_ui()

    # ── Theme ──────────────────────────────────────────────────────────
    @property
    def C(self):
        return THEME[self._mode]

    def _toggle_theme(self):
        if self._is_animating:
            return
        self._is_animating = True
        target = "light" if self._mode == "dark" else "dark"
        self._mode = target
        ctk.set_appearance_mode(target)
        icon = "\u2600\ufe0f  Light Mode" if target == "light" else "\U0001f319  Dark Mode"
        self._theme_btn.configure(text=icon)
        self._repaint()
        self._is_animating = False

    def _repaint(self):
        C = self.C
        self.configure(fg_color=C["bg"])
        # Sidebar
        self._sidebar.configure(fg_color=C["sidebar"])
        for d in self._dividers:
            d.configure(fg_color=C["divider"])
        self._logo_lbl.configure(text_color=C["accent"])
        self._logo_icon.configure(text_color=C["accent"])
        self._app_sub_lbl.configure(text_color=C["subtext"])
        self._nav_lbl.configure(text_color=C["subtext"])
        self._model_lbl.configure(text_color=C["subtext"])
        self._theme_btn.configure(fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"], text_color=C["text"])
        self._train_btn.configure(fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"], text_color=C["text"])
        self._train_row.configure(fg_color='transparent')
        self._version_lbl.configure(text_color=C["subtext"])
        # Nav
        self._btn_analysis.configure(
            fg_color=C["nav_active"] if self._current_view == "analysis" else C["nav_idle"],
            text_color="#ffffff" if self._current_view == "analysis" else C["text"],
            hover_color=C["accent_hv"])
        self._btn_reports.configure(
            fg_color=C["nav_active"] if self._current_view == "reports" else C["nav_idle"],
            text_color="#ffffff" if self._current_view == "reports" else C["text"],
            hover_color=C["accent_hv"])
        for rb in self._radio_buttons:
            rb.configure(text_color=C["text"], fg_color=C["accent"], border_color=C["border"])
        # Header
        self._header_frame.configure(fg_color=C["sidebar"])
        self._header_label.configure(text_color=C["text"])
        # Main
        self._main_frame.configure(fg_color=C["bg"])
        self._status_label.configure(text_color=C["subtext"])
        # Footer
        self._footer_frame.configure(fg_color=C["footer"])
        self._footer_lbl.configure(text_color=C["subtext"], fg_color=C["footer"])
        # Analysis view
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
        # Sample cards
        for card in self._sample_cards:
            card.repaint()
        # Donut
        self._donut.update_colors(bg=C["card"], track=C["donut_bg"], ham_c=C["ham"], spam_c=C["spam"])
        # Spinners
        self._analyze_spinner.update_colors(bg=C["bg"], color=C["loader"])
        self._train_spinner.update_colors(bg=C["btn_sec"], color=C["loader"])
        # Reports
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

    # ── Sidebar ────────────────────────────────────────────────────────
    def _build_sidebar(self):
        C = self.C
        self._sidebar = ctk.CTkFrame(
            self, width=260, corner_radius=0,
            fg_color=C["sidebar"], border_width=1, border_color=C["border"]
        )
        self._sidebar.grid(row=0, column=0, sticky='nsew')
        self._sidebar.grid_propagate(False)
        self._sidebar.grid_columnconfigure(0, weight=1)
        self._dividers = []

        # Logo
        logo_row = ctk.CTkFrame(self._sidebar, fg_color='transparent')
        logo_row.grid(row=0, column=0, padx=18, pady=(26, 2), sticky='w')

        self._logo_icon = ctk.CTkLabel(
            logo_row, text="\u2709",
            font=ctk.CTkFont(size=26), text_color=C["accent"]
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
        self._app_sub_lbl.grid(row=1, column=0, padx=20, pady=(0, 16), sticky='w')

        d1 = ctk.CTkFrame(self._sidebar, height=1, fg_color=C["divider"])
        d1.grid(row=2, column=0, padx=14, sticky='ew')
        self._dividers.append(d1)

        # Nav
        self._nav_lbl = ctk.CTkLabel(
            self._sidebar, text="NAVIGATION",
            font=ctk.CTkFont(family='Segoe UI', size=9, weight='bold'),
            text_color=C["subtext"]
        )
        self._nav_lbl.grid(row=3, column=0, padx=20, pady=(14, 6), sticky='w')

        self._btn_analysis = ctk.CTkButton(
            self._sidebar, text="\u2709  Email Analysis",
            command=lambda: self._switch_view('analysis'),
            height=38, corner_radius=8, anchor='w',
            fg_color=C["nav_active"], hover_color=C["accent_hv"],
            text_color="#ffffff",
            font=ctk.CTkFont(family='Segoe UI', size=12, weight='bold')
        )
        self._btn_analysis.grid(row=4, column=0, padx=12, pady=3, sticky='ew')

        self._btn_reports = ctk.CTkButton(
            self._sidebar, text="\U0001f4ca  Model Reports",
            command=lambda: self._switch_view('reports'),
            height=38, corner_radius=8, anchor='w',
            fg_color=C["nav_idle"], hover_color=C["accent_hv"],
            text_color=C["text"],
            font=ctk.CTkFont(family='Segoe UI', size=12)
        )
        self._btn_reports.grid(row=5, column=0, padx=12, pady=3, sticky='ew')

        d2 = ctk.CTkFrame(self._sidebar, height=1, fg_color=C["divider"])
        d2.grid(row=6, column=0, padx=14, pady=(14, 0), sticky='ew')
        self._dividers.append(d2)

        # Model selector
        self._model_lbl = ctk.CTkLabel(
            self._sidebar, text="SELECT MODEL",
            font=ctk.CTkFont(family='Segoe UI', size=9, weight='bold'),
            text_color=C["subtext"]
        )
        self._model_lbl.grid(row=7, column=0, padx=20, pady=(14, 6), sticky='w')

        self._radio_buttons = []
        for i, (label, value) in enumerate([
            ("Naive Bayes",            "naive_bayes"),
            ("Support Vector Machine", "svm"),
            ("Neural Network",         "neural_network"),
        ]):
            rb = ctk.CTkRadioButton(
                self._sidebar, text=f"  {label}",
                variable=self._selected_model, value=value,
                font=ctk.CTkFont(family='Segoe UI', size=12),
                text_color=C["text"], fg_color=C["accent"],
                border_color=C["border"]
            )
            rb.grid(row=8 + i, column=0, padx=24, pady=4, sticky='w')
            self._radio_buttons.append(rb)

        d3 = ctk.CTkFrame(self._sidebar, height=1, fg_color=C["divider"])
        d3.grid(row=11, column=0, padx=14, pady=(14, 0), sticky='ew')
        self._dividers.append(d3)

        # Theme toggle
        self._theme_btn = ctk.CTkButton(
            self._sidebar, text="\U0001f319  Dark Mode",
            command=self._toggle_theme, height=36,
            fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"],
            text_color=C["text"],
            font=ctk.CTkFont(family='Segoe UI', size=11), corner_radius=8
        )
        self._theme_btn.grid(row=12, column=0, padx=12, pady=(12, 4), sticky='ew')

        # Train + spinner
        self._train_row = ctk.CTkFrame(self._sidebar, fg_color='transparent')
        self._train_row.grid(row=13, column=0, padx=12, pady=4, sticky='ew')
        self._train_row.grid_columnconfigure(0, weight=1)

        self._train_btn = ctk.CTkButton(
            self._train_row, text="\u26a1  Train Models",
            command=self._train_models, height=36,
            fg_color=C["btn_sec"], hover_color=C["btn_sec_hv"],
            text_color=C["text"],
            font=ctk.CTkFont(family='Segoe UI', size=11), corner_radius=8
        )
        self._train_btn.grid(row=0, column=0, sticky='ew')

        self._train_spinner = LoaderSpinner(
            self._train_row, bg_color=C["btn_sec"], color=C["loader"]
        )
        self._train_spinner.grid(row=0, column=1, padx=(6, 0))

        d4 = ctk.CTkFrame(self._sidebar, height=1, fg_color=C["divider"])
        d4.grid(row=14, column=0, padx=14, pady=(12, 0), sticky='ew')
        self._dividers.append(d4)

        self._version_lbl = ctk.CTkLabel(
            self._sidebar, text=APP_VERSION,
            font=ctk.CTkFont(family='Consolas', size=9),
            text_color=C["subtext"]
        )
        self._version_lbl.grid(row=15, column=0, padx=20, pady=(8, 20), sticky='w')

    # ── Main Container ─────────────────────────────────────────────────
    def _build_main(self):
        C = self.C
        self._main_frame = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        self._main_frame.grid(row=0, column=1, sticky='nsew')
        self._main_frame.grid_rowconfigure(1, weight=1)
        self._main_frame.grid_columnconfigure(0, weight=1)

        # Header bar
        self._header_frame = ctk.CTkFrame(
            self._main_frame, fg_color=C["sidebar"], height=58, corner_radius=0
        )
        self._header_frame.grid(row=0, column=0, sticky='ew')
        self._header_frame.grid_propagate(False)
        self._header_frame.grid_columnconfigure(0, weight=1)

        self._header_label = ctk.CTkLabel(
            self._header_frame, text="\u2709  Email Analysis",
            font=ctk.CTkFont(family='Segoe UI', size=14, weight='bold'),
            text_color=C["text"]
        )
        self._header_label.grid(row=0, column=0, padx=28, pady=16, sticky='w')

        # Views
        self._view_analysis = self._build_analysis_view(self._main_frame)
        self._view_reports  = self._build_reports_view(self._main_frame)

        # Status bar
        self._status_label = ctk.CTkLabel(
            self._main_frame, text="\u2022  Ready",
            font=ctk.CTkFont(family='Consolas', size=10),
            text_color=C["subtext"]
        )
        self._status_label.grid(row=2, column=0, padx=28, pady=(2, 0), sticky='w')

        # Footer
        self._footer_frame = ctk.CTkFrame(
            self._main_frame, fg_color=C["footer"], height=32, corner_radius=0
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

    # ── Analysis View ──────────────────────────────────────────────────
    def _build_analysis_view(self, parent):
        C = self.C
        frame = ctk.CTkFrame(parent, fg_color=C["bg"])
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self._content_frame = ctk.CTkFrame(frame, fg_color=C["bg"])
        self._content_frame.grid(row=0, column=0, sticky='nsew', padx=24, pady=18)
        self._content_frame.grid_rowconfigure(0, weight=1)
        self._content_frame.grid_columnconfigure(0, weight=3)
        self._content_frame.grid_columnconfigure(1, weight=2)

        # ── Left panel ──
        self._left_panel = ctk.CTkFrame(self._content_frame, fg_color=C["bg"])
        self._left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
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

        # Button row
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

        self._analyze_spinner = LoaderSpinner(
            btn_row, bg_color=C["bg"], color=C["loader"]
        )
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
        self._result_card.grid(row=3, column=0, sticky='ew', pady=(14, 0))
        self._result_card.grid_columnconfigure(0, weight=1)
        self._result_card.grid_columnconfigure(1, weight=0)

        verdict_col = ctk.CTkFrame(self._result_card, fg_color='transparent')
        verdict_col.grid(row=0, column=0, sticky='w', padx=20, pady=16)

        self._verdict_label = ctk.CTkLabel(
            verdict_col, text="Awaiting Analysis",
            font=ctk.CTkFont(family='Segoe UI', size=16, weight='bold'),
            text_color=C["subtext"]
        )
        self._verdict_label.grid(row=0, column=0, sticky='w')

        self._model_info_label = ctk.CTkLabel(
            verdict_col, text="",
            font=ctk.CTkFont(family='Segoe UI', size=10),
            text_color=C["subtext"]
        )
        self._model_info_label.grid(row=1, column=0, sticky='w', pady=(4, 0))

        self._donut = DonutChart(self._result_card, bg_color=C["card"])
        self._donut.grid(row=0, column=1, padx=(0, 16), pady=12)

        # ── Right panel: sample emails ──
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
                theme_getter=lambda: self.C
            )
            card.grid(row=idx, column=0, sticky='ew', pady=4, padx=2)
            self._sample_cards.append(card)

        return frame

    # ── Reports View ───────────────────────────────────────────────────
    def _build_reports_view(self, parent):
        C = self.C
        self._reports_frame = ctk.CTkFrame(parent, fg_color=C["bg"])
        self._reports_frame.grid_rowconfigure(0, weight=1)
        self._reports_frame.grid_columnconfigure(0, weight=1)

        self._scroll_frame = ctk.CTkScrollableFrame(self._reports_frame, fg_color=C["bg"])
        self._scroll_frame.grid(row=0, column=0, sticky='nsew', padx=28, pady=20)
        self._scroll_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self._scroll_frame,
            text="\U0001f4ca  Model Performance Reports",
            font=ctk.CTkFont(family='Segoe UI', size=15, weight='bold'),
            text_color=C["text"]
        ).grid(row=0, column=0, sticky='w', pady=(0, 4))

        ctk.CTkLabel(
            self._scroll_frame,
            text="Evaluation of all trained classifiers on the SMS Spam Collection dataset.",
            font=ctk.CTkFont(family='Segoe UI', size=11),
            text_color=C["subtext"]
        ).grid(row=1, column=0, sticky='w', pady=(0, 14))

        # Metrics table
        self._metrics_frame = ctk.CTkFrame(
            self._scroll_frame, fg_color=C["card"],
            corner_radius=10, border_width=1, border_color=C["border"]
        )
        self._metrics_frame.grid(row=2, column=0, sticky='ew', pady=(0, 14))
        self._metrics_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self._metric_header_lbls = []
        for col, h in enumerate(['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score']):
            lbl = ctk.CTkLabel(
                self._metrics_frame, text=h,
                font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
                text_color=C["accent"]
            )
            lbl.grid(row=0, column=col, padx=16, pady=12, sticky='w')
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
            ml.grid(row=r_idx + 2, column=0, padx=16, pady=10, sticky='w')
            self._metric_model_lbls.append(ml)
            row_lbls = []
            for col in range(1, 5):
                lbl = ctk.CTkLabel(
                    self._metrics_frame, text="--",
                    font=ctk.CTkFont(family='Consolas', size=12),
                    text_color=C["subtext"]
                )
                lbl.grid(row=r_idx + 2, column=col, padx=16, pady=10, sticky='w')
                row_lbls.append(lbl)
            self._metric_rows.append(row_lbls)

        # Refresh row
        ref_row = ctk.CTkFrame(self._scroll_frame, fg_color='transparent')
        ref_row.grid(row=3, column=0, sticky='w', pady=(0, 22))

        self._refresh_btn = ctk.CTkButton(
            ref_row, text="\u27f3  Load / Refresh Results",
            command=self._load_reports, height=38,
            fg_color=C["accent"], hover_color=C["accent_hv"],
            corner_radius=8,
            font=ctk.CTkFont(family='Segoe UI', size=12)
        )
        self._refresh_btn.grid(row=0, column=0)

        self._reports_spinner = LoaderSpinner(
            ref_row, bg_color=C["bg"], color=C["loader"]
        )
        self._reports_spinner.grid(row=0, column=1, padx=(10, 0))

        # Confusion matrices
        self._cm_title_lbl = ctk.CTkLabel(
            self._scroll_frame, text="\U0001f5bc  Confusion Matrices",
            font=ctk.CTkFont(family='Segoe UI', size=13, weight='bold'),
            text_color=C["text"]
        )
        self._cm_title_lbl.grid(row=4, column=0, sticky='w', pady=(0, 10))

        self._cm_grid = ctk.CTkFrame(self._scroll_frame, fg_color='transparent')
        self._cm_grid.grid(row=5, column=0, sticky='ew')
        self._cm_grid.grid_columnconfigure((0, 1, 2), weight=1)

        self._cm_labels = []
        for col, title in enumerate(['Naive Bayes', 'SVM', 'Neural Network']):
            ctk.CTkLabel(
                self._cm_grid, text=title,
                font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
                text_color=C["subtext"]
            ).grid(row=0, column=col, pady=(0, 6))
            lbl = ctk.CTkLabel(
                self._cm_grid,
                text="[ Run training to generate ]",
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

    # ── Sample Emails ──────────────────────────────────────────────────
    def _load_sample(self, body: str):
        self._text_input.delete('0.0', 'end')
        self._text_input.insert('0.0', body)
        self._text_input.configure(text_color=self.C["text"])
        self._set_status("\u2022  Sample email loaded. Click Analyze.")

    # ── Reports Logic ──────────────────────────────────────────────────
    def _load_reports(self):
        if not models_exist():
            self._set_status("\u26a0  Models not found. Train models first.")
            return
        self._set_status("\u23f3  Loading report data...")
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
            self.after(0, self._set_status, "\u2714  Reports loaded successfully.")
        except Exception as e:
            self.after(0, self._reports_spinner.stop)
            self.after(0, self._set_status, f"\u26a0  Error: {e}")

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
            paths = ['reports/cm_naive_bayes.png', 'reports/cm_svm.png', 'reports/cm_neural_network.png']
            for lbl, fpath in zip(self._cm_labels, paths):
                if os.path.exists(fpath):
                    img   = PILImage.open(fpath).resize((290, 240))
                    ctk_i = ctk.CTkImage(light_image=img, dark_image=img, size=(290, 240))
                    lbl.configure(image=ctk_i, text="")
                    lbl._ctk_image = ctk_i
        except ImportError:
            self._set_status("\u26a0  Install Pillow: pip install Pillow")

    # ── Analysis Logic ─────────────────────────────────────────────────
    def _analyze(self):
        text = self._text_input.get('0.0', 'end').strip()
        if not text or text == PLACEHOLDER:
            messagebox.showwarning("Input Required", "Please enter email content to analyze.")
            return
        if not models_exist():
            messagebox.showerror("Models Not Found",
                                 "Trained models not found.\nClick '\u26a1 Train Models' first.")
            return
        self._set_status("\u23f3  Analyzing...")
        self._analyze_spinner.start()
        self._verdict_label.configure(text="Analyzing...", text_color=self.C["subtext"],
                                       font=ctk.CTkFont(family='Segoe UI', size=14))
        self._model_info_label.configure(text="")
        self._donut.set_values(0, 0, "", "")
        threading.Thread(target=self._run_prediction, args=(text,), daemon=True).start()

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
            text=f"{icon}  {label.upper()}   {confidence}% Confidence",
            font=ctk.CTkFont(family='Segoe UI', size=16, weight='bold'),
            text_color=color
        )
        self._model_info_label.configure(
            text=f"Model: {model_name}  \u00b7  Ham: {ham_prob}%  \u00b7  Spam: {spam_prob}%"
        )
        self._donut.set_values(
            ham_pct=ham_prob, spam_pct=spam_prob,
            label=f"{label}\n{confidence}%",
            sub="confidence"
        )
        self._set_status(f"\u2714  Done  |  Ham: {ham_prob}%  |  Spam: {spam_prob}%")

    def _show_error(self, error):
        messagebox.showerror("Prediction Error", f"Prediction failed:\n{error}")
        self._set_status("\u26a0  Error occurred.")
        self._verdict_label.configure(text="Analysis failed.", text_color=self.C["spam"])

    def _train_models(self):
        self._set_status("\u23f3  Training models... please wait.")
        self._train_spinner.start()
        threading.Thread(target=self._run_training, daemon=True).start()

    def _run_training(self):
        try:
            from src.train import train_all
            train_all()
            self.after(0, self._train_spinner.stop)
            self.after(0, self._set_status, "\u2714  All models trained successfully.")
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
            font=ctk.CTkFont(family='Segoe UI', size=16, weight='bold'),
            text_color=self.C["subtext"]
        )
        self._model_info_label.configure(text="")
        self._donut.set_values(0, 0, "", "")
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


# ── Entry Point ───────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = SpamDetectorApp()
    app.mainloop()
