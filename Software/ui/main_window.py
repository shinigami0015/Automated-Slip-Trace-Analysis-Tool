# -*- coding: utf-8 -*-
"""
STRCRYST -- Premium Main Window
AAA Future-Proof UI with Theme Engine, Session Memory, and Windows Controls.
"""
import os
import sys
import math
import shutil

from PyQt6.QtCore import (Qt, QTimer, QPointF, pyqtSlot, QPropertyAnimation, QEasingCurve, pyqtProperty)
from PyQt6.QtGui  import (QPainter, QColor, QRadialGradient, QPen, QBrush, QFont, QPolygonF)
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QPushButton, QComboBox, QDoubleSpinBox,
    QTextEdit, QFrame, QSizePolicy, QMessageBox, QFileDialog,
    QGridLayout, QStackedWidget, QProgressBar, QSizeGrip
)

from ui.styles       import get_stylesheet, get_status_style, get_theme_colors
from ui.title_bar    import TitleBar
from ui.thumbnail_widget import ThumbnailWidget
from core.matlab_worker  import MatlabWorker
from core.settings   import load_settings, save_settings


def _hline():
    f = QFrame(); f.setFrameShape(QFrame.Shape.HLine); return f

def _spacer(h: int = 8) -> QWidget:
    w = QWidget(); w.setFixedHeight(h); return w

# ══════════════════════════════════════════════════════════════════════════════
class StatusIndicator(QWidget):
    """Animated pill badge: coloured dot + status text."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._status  = "Ready"
        self._dot_col = QColor("#545456")
        self._pulse   = 0.0
        self._pulse_dir = 1.0
        self.is_dark_mode = True

        self.setFixedHeight(32)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._tick)

    def set_theme(self, is_dark: bool):
        self.is_dark_mode = is_dark
        self.set_status(self._status)

    def set_status(self, status: str):
        self._status = status
        _, dot_hex = get_status_style(status, self.is_dark_mode)
        self._dot_col = QColor(dot_hex)
        if status == "Running...":
            self._timer.start()
        else:
            self._timer.stop()
            self._pulse = 0.0
        self.update()

    def _tick(self):
        self._pulse += 0.06 * self._pulse_dir
        if self._pulse >= 1.0: self._pulse_dir = -1.0
        elif self._pulse <= 0.0: self._pulse_dir = 1.0
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()

        pill_style, dot_hex = get_status_style(self._status, self.is_dark_mode)
        bg_hex = pill_style.split("background:")[1].split(";")[0].strip() if "background:" in pill_style else "#2C2C2E"
        
        p.setBrush(QColor(bg_hex))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, W, H, H // 2, H // 2)

        dot_r, dot_cx, dot_cy = 5, 16, H // 2
        if self._status == "Running...":
            pg = QRadialGradient(dot_cx, dot_cy, dot_r * 3)
            pg.setColorAt(0.0, QColor(self._dot_col.red(), self._dot_col.green(), self._dot_col.blue(), int(160 * self._pulse)))
            pg.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(pg))
            p.drawEllipse(dot_cx - dot_r*3, dot_cy - dot_r*3, dot_r*6, dot_r*6)

        p.setBrush(self._dot_col)
        p.drawEllipse(dot_cx - dot_r, dot_cy - dot_r, dot_r*2, dot_r*2)

        f = QFont("Segoe UI", 9, QFont.Weight.Medium)
        p.setFont(f)
        tc = pill_style.split("color:")[1].split(";")[0].strip() if "color:" in pill_style else "#8E8E93"
        p.setPen(QColor(tc))
        p.drawText(dot_cx + dot_r + 8, 0, W - dot_cx - dot_r - 16, H,
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self._status)
        p.end()

# ══════════════════════════════════════════════════════════════════════════════
class FolderPickerRow(QWidget):
    def __init__(self, label: str, placeholder: str, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(5)

        lbl = QLabel(label.upper())
        lbl.setObjectName("sectionLabel")
        v.addWidget(lbl)

        h = QHBoxLayout()
        h.setSpacing(6)
        h.setContentsMargins(0, 0, 0, 0)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(placeholder)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("browseBtn")
        browse_btn.setFixedWidth(62)
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._browse)

        h.addWidget(self.path_edit, 1)
        h.addWidget(browse_btn)
        v.addLayout(h)

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", self.path_edit.text() or os.path.expanduser("~"))
        if folder: self.path_edit.setText(folder)
    def text(self) -> str: return self.path_edit.text().strip()
    def setText(self, t: str): self.path_edit.setText(t)

# ══════════════════════════════════════════════════════════════════════════════
class SidebarHeader(QWidget):
    H = 88
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarHeader")
        self.setFixedHeight(self.H)
        self._dot_angle = 0.0
        self.is_dark_mode = True
        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def set_theme(self, is_dark: bool):
        self.is_dark_mode = is_dark
        self.update()

    def _tick(self):
        self._dot_angle = (self._dot_angle + 1.8) % 360.0
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.H

        c = get_theme_colors(self.is_dark_mode)
        p.setBrush(QColor(c['BG_TITLEBAR']))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(self.rect())

        p.setPen(QPen(QColor(c['BORDER_DIM']), 1))
        p.drawLine(0, H - 1, W, H - 1)

        cx, cy, r = 34, H // 2, 18
        def pts(radius): return [QPointF(cx + radius * math.cos(math.radians(60*k - 30)), cy + radius * math.sin(math.radians(60*k - 30))) for k in range(6)]

        # Crystal
        accent_r, accent_g, accent_b = QColor(c['ACCENT']).getRgb()[:3]
        ag = QRadialGradient(cx, cy, r * 2)
        ag.setColorAt(0.0, QColor(accent_r, accent_g, accent_b, 50))
        ag.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(ag))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(cx-r*2), int(cy-r*2), int(r*4), int(r*4))

        for radius, alpha, width in [(r, 200, 1.2), (r*0.58, 130, 0.8)]:
            p.setPen(QPen(QColor(accent_r, accent_g, accent_b, alpha), width))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolygon(QPolygonF(pts(radius)))

        p.setPen(QPen(QColor(accent_r, accent_g, accent_b, 100), 0.6))
        for k in range(6):
            p.drawLine(pts(r)[k], pts(r*0.58)[k])
            p.drawLine(pts(r*0.58)[k], QPointF(cx, cy))

        ar = math.radians(self._dot_angle - 30)
        dx, dy = cx + r * math.cos(ar), cy + r * math.sin(ar)
        dg = QRadialGradient(dx, dy, 7)
        dg.setColorAt(0.0, QColor(accent_r, accent_g, accent_b, 200))
        dg.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(dg)); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(dx-7), int(dy-7), 14, 14)
        p.setBrush(QColor(c['TEXT_1']))
        p.drawEllipse(int(dx-2), int(dy-2), 4, 4)

        cg = QRadialGradient(cx, cy, 8)
        cg.setColorAt(0.0, QColor(accent_r, accent_g, accent_b, 220))
        cg.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(cg))
        p.drawEllipse(cx-8, cy-8, 16, 16)
        p.setBrush(QColor(c['TEXT_1']))
        p.drawEllipse(cx-2, cy-2, 4, 4)

        tf = QFont("Segoe UI", 14, QFont.Weight.Light)
        tf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
        p.setFont(tf)
        p.setPen(QColor(c['TEXT_1']))
        p.drawText(cx + r + 16, 14, W - cx - r - 24, 32, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "STRCRYST")

        sf = QFont("Segoe UI", 7)
        sf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
        p.setFont(sf)
        p.setPen(QColor(c['TEXT_2']))
        p.drawText(cx + r + 16, 46, W - cx - r - 24, 20, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "SLIP TRACE ANALYSIS")
        p.end()

# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self._worker: MatlabWorker | None = None
        self._settings = load_settings()
        self._is_dark = self._settings.get("is_dark_mode", True)
        self._current_tab = 0

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setMinimumSize(1160, 760)
        self.resize(1340, 860)

        self._build_ui()
        self._apply_theme()
        self._enable_shadow()
        self._load_session_data()

    def _enable_shadow(self):
        if sys.platform == "win32":
            try:
                from ctypes import windll, c_int, byref, sizeof
                windll.dwmapi.DwmSetWindowAttribute(int(self.winId()), 2, byref(c_int(1)), sizeof(c_int))
            except: pass

    # ── Theme ──────────────────────────────────────────────────────────────────
    def _apply_theme(self):
        self.setStyleSheet(get_stylesheet(self._is_dark))
        self._title_bar.set_theme(self._is_dark)
        self._sidebar_header.set_theme(self._is_dark)
        self._status_ind.set_theme(self._is_dark)
        self._theme_btn.setText("☀ Light Mode" if self._is_dark else "🌙 Dark Mode")
        
        c = get_theme_colors(self._is_dark)
        self.centralWidget().setStyleSheet(f"background: {c['BG_APP']};")
        self.body.setStyleSheet(f"background: {c['BG_APP']};")
        
        self._settings["is_dark_mode"] = self._is_dark
        save_settings(self._settings)

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        self._apply_theme()

    # ── Construction ───────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        self._title_bar = TitleBar()
        self._title_bar.closeRequested.connect(self.close)
        self._title_bar.minimizeRequested.connect(self.showMinimized)
        self._title_bar.maximizeRequested.connect(self._toggle_maximize)
        v.addWidget(self._title_bar)

        self.body = QWidget()
        h = QHBoxLayout(self.body)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        h.addWidget(self._build_sidebar())
        h.addWidget(self._build_content(), 1)
        v.addWidget(self.body, 1)
        v.addWidget(self._build_statusbar())

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(312)
        sv = QVBoxLayout(sidebar)
        sv.setContentsMargins(0, 0, 0, 0)
        sv.setSpacing(0)

        self._sidebar_header = SidebarHeader()
        sv.addWidget(self._sidebar_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        inner = QWidget()
        iv = QVBoxLayout(inner)
        iv.setContentsMargins(18, 18, 18, 18)
        iv.setSpacing(0)

        # ── PROJECT ──
        iv.addWidget(self._section_label("Project"))
        iv.addWidget(_spacer(10))
        self.scripts_picker = FolderPickerRow("Scripts Folder", "Path to .m files...")
        self.input_picker   = FolderPickerRow("Input Folder", "Folder with .ctf files...")
        self.output_picker  = FolderPickerRow("Output Folder", "Results will be saved here...")
        self.scripts_picker.path_edit.textChanged.connect(self._save_session_data)
        self.input_picker.path_edit.textChanged.connect(self._save_session_data)
        self.output_picker.path_edit.textChanged.connect(self._save_session_data)

        iv.addWidget(self.scripts_picker)
        iv.addWidget(_spacer(14))
        iv.addWidget(self.input_picker)
        iv.addWidget(_spacer(14))
        iv.addWidget(self.output_picker)
        iv.addWidget(_spacer(22))

        # ── PARAMETERS ──
        iv.addWidget(_hline())
        iv.addWidget(_spacer(18))
        iv.addWidget(self._section_label("Analysis Parameters"))
        iv.addWidget(_spacer(12))

        iv.addWidget(self._field_label("Loading Direction"))
        iv.addWidget(_spacer(5))
        self.loading_combo = QComboBox()
        self.loading_combo.addItems(["X", "Y", "Z"])
        self.loading_combo.currentTextChanged.connect(self._save_session_data)
        iv.addWidget(self.loading_combo)
        iv.addWidget(_spacer(14))

        # Collapsible Advanced Section
        self._adv_btn = QPushButton("Advanced Parameters ▼")
        self._adv_btn.setObjectName("linkBtn")
        self._adv_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._adv_btn.setStyleSheet("text-align: left;")
        self._adv_btn.clicked.connect(self._toggle_advanced)
        iv.addWidget(self._adv_btn)

        self._adv_widget = QWidget()
        adv_l = QVBoxLayout(self._adv_widget)
        adv_l.setContentsMargins(10, 10, 0, 0)
        
        adv_l.addWidget(self._field_label("c/a Ratio"))
        adv_l.addWidget(_spacer(5))
        self.ca_spin = QDoubleSpinBox()
        self.ca_spin.setRange(0.1, 10.0)
        self.ca_spin.setSingleStep(0.001)
        self.ca_spin.setDecimals(4)
        self.ca_spin.valueChanged.connect(self._save_session_data)
        adv_l.addWidget(self.ca_spin)
        adv_l.addWidget(_spacer(14))

        adv_l.addWidget(self._field_label("Crystal System"))
        adv_l.addWidget(_spacer(5))
        self.crystal_combo = QComboBox()
        self.crystal_combo.addItems(["HCP + BCC", "HCP only", "BCC only"])
        self.crystal_combo.currentTextChanged.connect(self._save_session_data)
        adv_l.addWidget(self.crystal_combo)
        
        self._adv_widget.setVisible(False)
        iv.addWidget(self._adv_widget)

        iv.addStretch()
        scroll.setWidget(inner)
        sv.addWidget(scroll, 1)
        sv.addWidget(self._build_controls_panel())
        return sidebar

    def _toggle_advanced(self):
        viz = not self._adv_widget.isVisible()
        self._adv_widget.setVisible(viz)
        self._adv_btn.setText("Advanced Parameters ▲" if viz else "Advanced Parameters ▼")

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text.upper()); lbl.setObjectName("sectionLabel"); return lbl

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text); lbl.setObjectName("fieldLabel"); return lbl

    def _build_controls_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("controlsPanel")
        pv = QVBoxLayout(panel)
        pv.setContentsMargins(18, 16, 18, 18)
        pv.setSpacing(10)

        self._status_ind = StatusIndicator()
        pv.addWidget(self._status_ind)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background: transparent; border: none; }
            QProgressBar::chunk { background: #0A84FF; border-radius: 1px; }
        """)
        self.progress_bar.setVisible(False)
        pv.addWidget(self.progress_bar)

        self.run_btn = QPushButton("▶  Run Analysis")
        self.run_btn.setObjectName("runBtn")
        self.run_btn.setMinimumHeight(46)
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_btn.clicked.connect(self._on_run)
        pv.addWidget(self.run_btn)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.abort_btn = QPushButton("Abort")
        self.abort_btn.setObjectName("ghostBtn")
        self.abort_btn.setEnabled(False)
        self.abort_btn.clicked.connect(self._on_abort)
        self.open_output_btn = QPushButton("📂 Output Folder")
        self.open_output_btn.setObjectName("accentGhostBtn")
        self.open_output_btn.setEnabled(False)
        self.open_output_btn.clicked.connect(self._open_output_folder)
        btn_row.addWidget(self.abort_btn)
        btn_row.addWidget(self.open_output_btn, 1)
        pv.addLayout(btn_row)
        return panel

    def _build_content(self) -> QWidget:
        area = QWidget(); area.setObjectName("contentArea")
        av = QVBoxLayout(area)
        av.setContentsMargins(0, 0, 0, 0)
        av.setSpacing(0)

        tab_bar = QWidget()
        tab_bar.setObjectName("tabBar")
        tab_bar.setFixedHeight(44)
        tbl = QHBoxLayout(tab_bar)
        tbl.setContentsMargins(18, 0, 18, 0)
        tbl.setSpacing(0)

        self._btn_outputs = QPushButton("Generated Outputs")
        self._btn_outputs.setObjectName("tabBtn")
        self._btn_outputs.setProperty("active", "true")
        self._btn_outputs.clicked.connect(lambda: self._switch_tab(0))

        self._btn_console = QPushButton("Console Log")
        self._btn_console.setObjectName("tabBtn")
        self._btn_console.setProperty("active", "false")
        self._btn_console.clicked.connect(lambda: self._switch_tab(1))

        tbl.addWidget(self._btn_outputs)
        tbl.addWidget(self._btn_console)
        tbl.addStretch()

        self._export_btn = QPushButton("📦 Zip Results")
        self._export_btn.setObjectName("iconBtn")
        self._export_btn.clicked.connect(self._zip_results)
        
        self._refresh_btn = QPushButton("↻ Refresh")
        self._refresh_btn.setObjectName("iconBtn")
        self._refresh_btn.clicked.connect(self._refresh_thumbnails)

        self._clear_log_btn = QPushButton("Clear")
        self._clear_log_btn.setObjectName("iconBtn")
        self._clear_log_btn.clicked.connect(lambda: self.log_edit.clear())

        tbl.addWidget(self._export_btn)
        tbl.addWidget(self._refresh_btn)
        tbl.addWidget(self._clear_log_btn)
        av.addWidget(tab_bar)

        self._stack = QStackedWidget()
        av.addWidget(self._stack, 1)
        self._stack.addWidget(self._build_outputs_page())
        self._stack.addWidget(self._build_console_page())
        self._switch_tab(0)
        return area

    def _build_outputs_page(self) -> QWidget:
        page = QWidget()
        pv = QVBoxLayout(page)
        pv.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.thumb_container = QWidget()
        self.thumb_grid = QGridLayout(self.thumb_container)
        self.thumb_grid.setSpacing(14)
        self.thumb_grid.setContentsMargins(22, 22, 22, 22)
        self._placeholder_lbl = QLabel("Run the analysis to generate outputs.")
        self._placeholder_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder_lbl.setStyleSheet("color: #8E8E93; font-size: 11pt;")
        self.thumb_grid.addWidget(self._placeholder_lbl, 0, 0, 1, 3)
        scroll.setWidget(self.thumb_container)
        pv.addWidget(scroll)
        return page

    def _build_console_page(self) -> QWidget:
        page = QWidget()
        pv = QVBoxLayout(page)
        pv.setContentsMargins(0, 0, 0, 0)
        self.log_edit = QTextEdit()
        self.log_edit.setObjectName("consoleLog")
        self.log_edit.setReadOnly(True)
        self.log_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        pv.addWidget(self.log_edit)
        return page

    def _build_statusbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(26)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(14, 0, 6, 0)
        bl.setSpacing(10)
        
        self._theme_btn = QPushButton("🌙 Dark Mode")
        self._theme_btn.setObjectName("linkBtn")
        self._theme_btn.clicked.connect(self._toggle_theme)
        bl.addWidget(self._theme_btn)

        bl.addStretch()
        lbl = QLabel("v1.1.0  ·  IISc Materials Lab")
        lbl.setStyleSheet("color: #8E8E93; font-size: 8pt;")
        bl.addWidget(lbl)
        grip = QSizeGrip(self)
        bl.addWidget(grip)
        return bar

    def _switch_tab(self, idx: int):
        self._stack.setCurrentIndex(idx)
        self._btn_outputs.setProperty("active", "true" if idx == 0 else "false")
        self._btn_console.setProperty("active", "true" if idx == 1 else "false")
        for btn in (self._btn_outputs, self._btn_console):
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        self._export_btn.setVisible(idx == 0)
        self._refresh_btn.setVisible(idx == 0)
        self._clear_log_btn.setVisible(idx == 1)

    # ── Session / Validation ──
    @property
    def scripts_edit(self): return self.scripts_picker.path_edit
    @property
    def input_edit(self): return self.input_picker.path_edit
    @property
    def output_edit(self): return self.output_picker.path_edit

    def _load_session_data(self):
        self.scripts_picker.setText(self._settings.get("scripts_folder", ""))
        self.input_picker.setText(self._settings.get("input_folder", ""))
        self.output_picker.setText(self._settings.get("output_folder", ""))
        self.loading_combo.setCurrentText(self._settings.get("loading_direction", "X"))
        self.ca_spin.setValue(self._settings.get("ca_ratio", 1.5930))
        self.crystal_combo.setCurrentText(self._settings.get("crystal_system", "HCP + BCC"))

    def _save_session_data(self):
        self._settings.update({
            "scripts_folder": self.scripts_picker.text(),
            "input_folder": self.input_picker.text(),
            "output_folder": self.output_picker.text(),
            "loading_direction": self.loading_combo.currentText(),
            "ca_ratio": self.ca_spin.value(),
            "crystal_system": self.crystal_combo.currentText()
        })
        save_settings(self._settings)

    def _validate_inputs(self) -> bool:
        s, i, o = self.scripts_picker.text(), self.input_picker.text(), self.output_picker.text()
        if not s or not os.path.isdir(s): return self._err("Invalid Scripts", "Select a valid scripts folder.")
        if not i or not os.path.isdir(i): return self._err("Invalid Input", "Select a valid input folder.")
        if not o: return self._err("Invalid Output", "Specify an output folder.")
        if not os.path.exists(o): os.makedirs(o, exist_ok=True)
        return True

    def _err(self, t: str, m: str) -> bool: QMessageBox.critical(self, t, m); return False

    # ── Actions ──
    @pyqtSlot()
    def _on_run(self):
        try: import matlab.engine # noqa
        except: return self._err("Engine Not Found", "MATLAB Engine API for Python not installed.")
        if not self._validate_inputs(): return

        self.run_btn.setEnabled(False); self.abort_btn.setEnabled(True)
        self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
        self._switch_tab(1)

        self._worker = MatlabWorker(
            scripts_folder=self.scripts_picker.text(),
            input_folder=self.input_picker.text(), output_folder=self.output_picker.text(),
            loading_direction=self.loading_combo.currentText(),
            ca_ratio=self.ca_spin.value(), crystal_system=self.crystal_combo.currentText()
        )
        self._worker.log_line.connect(self._append_log)
        self._worker.status_changed.connect(self._status_ind.set_status)
        self._worker.finished_ok.connect(self._on_done)
        self._worker.finished_err.connect(self._on_err)
        self._worker.progress.connect(self.progress_bar.setValue)
        self._worker.start()

    @pyqtSlot()
    def _on_abort(self):
        if self._worker and self._worker.isRunning(): self._worker.abort()
        self.abort_btn.setEnabled(False)

    @pyqtSlot(str)
    def _append_log(self, l: str):
        self.log_edit.append(l); sb = self.log_edit.verticalScrollBar(); sb.setValue(sb.maximum())

    @pyqtSlot()
    def _on_done(self):
        self.run_btn.setEnabled(True); self.abort_btn.setEnabled(False)
        self.open_output_btn.setEnabled(True); self.progress_bar.setVisible(False)
        self._refresh_thumbnails(); self._switch_tab(0)

    @pyqtSlot(str)
    def _on_err(self, msg: str):
        self.run_btn.setEnabled(True); self.abort_btn.setEnabled(False)
        self.progress_bar.setVisible(False); self._err("Error", msg)

    def _refresh_thumbnails(self):
        out = self.output_picker.text()
        if not out or not os.path.isdir(out): return
        pngs = sorted([os.path.join(r, f) for r, _, fs in os.walk(out) for f in fs if f.lower().endswith(".png")])
        while self.thumb_grid.count():
            item = self.thumb_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        if not pngs:
            self._placeholder_lbl = QLabel("No PNG files found.")
            self._placeholder_lbl.setStyleSheet("color: #8E8E93; font-size: 11pt;")
            self.thumb_grid.addWidget(self._placeholder_lbl, 0, 0, 1, 3)
            return
        for i, p in enumerate(pngs):
            card = ThumbnailWidget(p, thumb_size=195)
            self.thumb_grid.addWidget(card, i // 3, i % 3)

    def _open_output_folder(self):
        out = self.output_picker.text()
        if os.path.isdir(out): os.startfile(out) if sys.platform.startswith("win") else None

    def _zip_results(self):
        out = self.output_picker.text()
        if not out or not os.path.isdir(out):
            return self._err("No Output Folder", "Please run analysis first.")
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Zip", os.path.join(out, "STRCRYST_Results.zip"), "Zip Files (*.zip)")
        if save_path:
            shutil.make_archive(save_path.replace(".zip", ""), 'zip', out)
            QMessageBox.information(self, "Success", f"Results zipped to:\n{save_path}")

    def fade_in(self):
        self.setWindowOpacity(0.0)
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(500); anim.setStartValue(0.0); anim.setEndValue(1.0)
        anim.start(); self._fadein_ref = anim

    def _toggle_maximize(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def closeEvent(self, e):
        if self._worker and self._worker.isRunning():
            self._worker.abort(); self._worker.wait(5000)
        e.accept()
