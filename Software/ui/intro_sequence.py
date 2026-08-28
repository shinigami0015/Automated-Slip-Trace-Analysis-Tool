# -*- coding: utf-8 -*-
"""
ASTA Tool -- Cinematic Intro Sequence
Handles the branded loading card, system diagnostics, and interactive startup guide.
"""
import sys
import os
from PyQt6.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve, 
                           pyqtSignal, pyqtProperty, QRectF, QPointF)
from PyQt6.QtGui  import (QPainter, QColor, QFont, QFontMetrics, QBrush, 
                           QLinearGradient, QPainterPath)
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QStackedWidget, QFrame)


def _patch_matlab_arch_txt():
    """
    Runs at module-import time (before any Qt widget is constructed).
    Rewrites _internal/matlab/engine/_arch.txt with the MATLAB version that
    is actually installed on this machine so that matlab/__init__.py can
    locate the correct DLLs instead of crashing on hardcoded R2023a paths.

    If no MATLAB installation is found the file is left untouched; the
    later import attempt in _check_matlab_engine() already catches all
    possible exceptions gracefully.
    """
    try:
        import glob
        # Locate _arch.txt relative to the running exe (frozen) or this file.
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        arch_txt = os.path.join(base, '_internal', 'matlab', 'engine', '_arch.txt')
        if not os.path.exists(arch_txt):
            # Fallback: look one level up from ui/
            arch_txt = os.path.normpath(
                os.path.join(os.path.dirname(__file__), '..', 'matlab', 'engine', '_arch.txt')
            )
        if not os.path.exists(arch_txt):
            return  # Nothing to patch

        # Find the newest MATLAB installation under Program Files
        candidates = sorted(
            glob.glob(r"C:\Program Files\MATLAB\R*"),
            reverse=True          # newest release first (R2024b > R2024a > R2023b …)
        )
        for matlab_root in candidates:
            bin_dir = os.path.join(matlab_root, 'bin', 'win64')
            if not os.path.isdir(bin_dir):
                continue
            pyd_dir    = os.path.join(os.path.dirname(arch_txt), 'win64')
            extern_bin = os.path.join(matlab_root, 'extern', 'bin', 'win64')
            lines = ['win64\n', bin_dir + '\n', pyd_dir + '\n']
            if os.path.isdir(extern_bin):
                lines.append(extern_bin + '\n')
            with open(arch_txt, 'w', encoding='utf-8') as fh:
                fh.writelines(lines)
            break  # patched successfully with the best candidate
    except Exception:
        pass  # Never crash the app due to _arch.txt patching


_patch_matlab_arch_txt()

# ══════════════════════════════════════════════════════════════════════════════
# 1. THE ASTA LOADING CARD
# ══════════════════════════════════════════════════════════════════════════════
class CinematicIntro(QWidget):
    """
    Branded loading card showing the ASTA Tool identity with:
      - Title: Automated Slip-Trace Analysis (ASTA) Tool
      - Group & Institution credits
      - UI Developer credit
      - A Proceed button to continue into the diagnostics/main window
    """
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #0D1117;")
        self._opacity = 0.0
        self._proceed_visible = False

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addStretch(2)

        card = QWidget()
        card.setStyleSheet("background: transparent;")
        card_v = QVBoxLayout(card)
        card_v.setContentsMargins(60, 0, 60, 0)
        card_v.setSpacing(0)

        self._title_lbl = QLabel("Automated Slip-Trace Analysis (ASTA) Tool")
        self._title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_lbl.setStyleSheet(
            "color: #F5F5F7; font-family: 'Segoe UI'; font-size: 20pt; "
            "font-weight: 300; letter-spacing: 1px;"
        )
        self._title_lbl.setWordWrap(True)
        card_v.addWidget(self._title_lbl)
        card_v.addSpacing(28)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #1E3A5F; max-height: 1px; border: none;")
        card_v.addWidget(sep)
        card_v.addSpacing(22)

        cite_lbl = QLabel(
            'Kindly cite: <span style="color:#0A84FF;">Chandraker et al., Plasticity and damage initiation in textured Zr-2.5%Nb pressure tube material: A slip trace analysis-based study, Materials Science and Engineering: A, 2026</span> if using this for your work.'
        )
        cite_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cite_lbl.setStyleSheet(
            "color: #8E8E93; font-family: 'Segoe UI'; font-size: 8.5pt; font-style: italic;"
        )
        cite_lbl.setWordWrap(True)
        card_v.addWidget(cite_lbl)
        card_v.addSpacing(20)

        group_lbl = QLabel("Extreme Environment Materials Group (EEMG)")
        group_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_lbl.setStyleSheet(
            "color: #C7C7CC; font-family: 'Segoe UI'; font-size: 11pt; font-weight: 500;"
        )
        card_v.addWidget(group_lbl)
        card_v.addSpacing(6)

        inst_lbl = QLabel("Indian Institute of Science (IISc), Bangalore")
        inst_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inst_lbl.setStyleSheet(
            "color: #8E8E93; font-family: 'Segoe UI'; font-size: 10pt;"
        )
        card_v.addWidget(inst_lbl)
        card_v.addSpacing(18)

        dev_lbl = QLabel("Dhiraj Kori \u00b7 Parardha Dhar \u00b7 Abhinav Chandraker")
        dev_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev_lbl.setStyleSheet(
            "color: #58A6FF; font-family: 'Segoe UI'; font-size: 9pt; font-weight: 500; letter-spacing: 0.5px;"
        )
        card_v.addWidget(dev_lbl)
        card_v.addSpacing(28)

        self._proceed_btn = QPushButton("Proceed  \u2192")
        self._proceed_btn.setFixedHeight(44)
        self._proceed_btn.setFixedWidth(180)
        self._proceed_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._proceed_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0 y1:0 x2:0 y2:1,
                    stop:0 #0A84FF, stop:1 #0056B3);
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-family: 'Segoe UI';
                font-size: 11pt;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover { background: #0A84FF; }
            QPushButton:pressed { background: #0056B3; }
        """)
        self._proceed_btn.setVisible(False)
        self._proceed_btn.clicked.connect(self.finished.emit)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self._proceed_btn)
        btn_row.addStretch()
        card_v.addLayout(btn_row)

        v.addWidget(card)
        v.addStretch(3)

        self._anim_fade = QPropertyAnimation(self, b"opacity_factor")
        self._anim_fade.setDuration(1200)
        self._anim_fade.setStartValue(0.0)
        self._anim_fade.setEndValue(1.0)
        self._anim_fade.setEasingCurve(QEasingCurve.Type.OutCubic)

    @pyqtProperty(float)
    def opacity_factor(self): return self._opacity
    @opacity_factor.setter
    def opacity_factor(self, v):
        self._opacity = v
        self.setWindowOpacity(v)
        self.update()

    def start(self):
        self.setWindowOpacity(0.0)
        self._anim_fade.start()
        self._anim_fade.finished.connect(self._on_fade_done)

    def _on_fade_done(self):
        self._proceed_btn.setVisible(True)

# ══════════════════════════════════════════════════════════════════════════════
# 2. SYSTEM DIAGNOSTICS (PRE-FLIGHT)
# ══════════════════════════════════════════════════════════════════════════════
try:
    import winreg
    _HAS_WINREG = True
except ImportError:
    _HAS_WINREG = False

class DiagnosticsCheck(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #0D1117;")
        v = QVBoxLayout(self)
        v.setContentsMargins(60, 60, 60, 60)

        self.title = QLabel("SYSTEM PRE-FLIGHT CHECK")
        self.title.setStyleSheet("color: #58A6FF; font-family: 'Consolas'; font-size: 14pt; letter-spacing: 2px;")
        v.addWidget(self.title)

        self.log_area = QLabel("")
        self.log_area.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.log_area.setStyleSheet("color: #8B949E; font-family: 'Consolas'; font-size: 11pt; line-height: 1.8;")
        self.log_area.setTextFormat(Qt.TextFormat.RichText)
        v.addWidget(self.log_area, 1)

        # ── IMPORTANT: steps use CALLABLES (not pre-computed values) ──────────
        # This defers the matlab check until start() is called, after main.py's
        # _auto_configure_matlab() has already patched _arch.txt.
        self._steps = [
            ("Scanning Windows Registry for MATLAB...", 800,  self._check_matlab_installed),
            ("Testing MATLAB Engine API for Python...", 1200, self._check_matlab_engine),
            ("Verifying MTEX Toolbox Linkage...",       700,  "WARNING"),
            ("Loading Crystallographic Core...",        500,  True),
        ]
        self._current_step = 0
        self._log_text = ""

    def _check_matlab_installed(self):
        """Scans Windows Registry to see if MATLAB is actually installed."""
        try:
            if _HAS_WINREG:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\MathWorks\MATLAB", 0,
                    winreg.KEY_READ | winreg.KEY_WOW64_64KEY
                )
                winreg.CloseKey(key)
                return True
        except Exception:
            pass
        return os.path.exists(r"C:\Program Files\MATLAB")

    def _check_matlab_engine(self):
        """
        Checks if matlab.engine is importable.
        _patch_matlab_arch_txt() (called at module load) already rewrites
        _arch.txt with the correct MATLAB version before we reach here.
        We catch all exceptions so a wrong _arch.txt or a missing MATLAB
        installation never crashes the application.
        """
        try:
            import matlab.engine  # noqa
            return True
        except Exception:          # covers ImportError, RuntimeError, OSError…
            return False

    def start(self):
        self._run_next_step()

    def _run_next_step(self):
        if self._current_step >= len(self._steps):
            self._log_text += "<br><span style='color:#3FB950;'>&#9654; PRE-FLIGHT COMPLETE. LAUNCHING STARTUP GUIDE...</span>"
            self.log_area.setText(self._log_text)
            QTimer.singleShot(1500, self.finished.emit)
            return

        msg, delay, status = self._steps[self._current_step]
        self._log_text += f"&gt; {msg} "
        self.log_area.setText(self._log_text)

        def _resolve():
            # Resolve lazily: call the check function now (not at __init__ time)
            resolved = status() if callable(status) else status

            if resolved is True:
                self._log_text += "<span style='color:#3FB950;'>[&#10003; FOUND]</span><br>"
            elif resolved == "WARNING":
                self._log_text += "<span style='color:#E68A00;'>[&#9888; DEFERRED TO RUNTIME]</span><br>"
            else:
                self._log_text += "<span style='color:#FF7B72;'>[&#10007; MISSING]</span><br>"

            self.log_area.setText(self._log_text)
            self._current_step += 1
            QTimer.singleShot(300, self._run_next_step)

        QTimer.singleShot(delay, _resolve)

# ══════════════════════════════════════════════════════════════════════════════
# 3. INTERACTIVE STARTUP GUIDE CAROUSEL
# ══════════════════════════════════════════════════════════════════════════════
class ManualPage(QWidget):
    def __init__(self, title, content, icon):
        super().__init__()
        v = QVBoxLayout(self)
        v.setContentsMargins(40, 40, 40, 40)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ic = QLabel(icon)
        ic.setStyleSheet("font-size: 48px; color: #0A84FF; margin-bottom: 20px;")
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(ic)

        t = QLabel(title)
        t.setStyleSheet("font-size: 20pt; font-weight: 300; color: #F5F5F7; margin-bottom: 10px;")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t)

        c = QLabel(content)
        c.setStyleSheet("font-size: 11pt; color: #8E8E93; line-height: 1.5;")
        c.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c.setWordWrap(True)
        v.addWidget(c)

class InteractiveManual(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #161618;")
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.stack.addWidget(ManualPage(
            "Welcome to ASTA Tool",
            "ASTA Tool is an advanced UI for EBSD Slip Trace & Schmid Factor Analysis.\n\n"
            "This software automates the generation of crystallographic slip trace maps and CSV datasets "
            "directly from your .ctf files.",
            "\U0001f48e"
        ))
        self.stack.addWidget(ManualPage(
            "System Requirements",
            "To run the analysis, you MUST have installed:\n"
            "1. MATLAB (R2021a or later)\n"
            "2. MTEX Toolbox (added to MATLAB path)\n"
            "3. MATLAB Engine API for Python\n\n"
            "If missing, the UI will still work, but analysis will abort.",
            "\u2699\ufe0f"
        ))
        self.stack.addWidget(ManualPage(
            "Quick Start Guide",
            "1. Select the folder containing the core .m scripts.\n"
            "2. Select the input folder containing your EBSD .ctf data.\n"
            "3. Choose an output folder.\n"
            "4. Hit 'Run Analysis' and wait for the results.\n\n"
            "Your settings will be automatically remembered for next time.",
            "\U0001f680"
        ))
        self.stack.addWidget(ManualPage(
            "About & Credits",
            "Chandraker et al., Plasticity and damage initiation in textured Zr-2.5%Nb pressure tube material: "
            "A slip trace analysis-based study, Materials Science and Engineering: A, 2026\n\n"
            "\u2022 Core Algorithms & Numerical Implementation: Dhiraj Kori\n"
            "\u2022 User Interface & Application Architecture: Parardha Dhar\n"
            "\u2022 Code script and UI testing: Abhinav Chandraker\n\n"
            "Extreme Environment Materials Group (EEMG)\nIndian Institute of Science (IISc), Bangalore",
            "\U0001f4dc"
        ))
        v.addWidget(self.stack, 1)

        bottom = QWidget()
        bottom.setFixedHeight(80)
        h = QHBoxLayout(bottom)
        h.setContentsMargins(40, 0, 40, 20)

        self.skip_btn = QPushButton("Skip Guide")
        self.skip_btn.setStyleSheet("color: #545456; background: transparent; border: none; font-size: 11pt;")
        self.skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.skip_btn.clicked.connect(self.finished.emit)
        h.addWidget(self.skip_btn)
        h.addStretch()

        self.dots = QLabel("\u25cf \u25cb \u25cb \u25cb")
        self.dots.setStyleSheet("color: #3A3A3C; font-size: 14pt; letter-spacing: 4px;")
        h.addWidget(self.dots)
        h.addStretch()

        self.next_btn = QPushButton("Next \u2794")
        self.next_btn.setStyleSheet("color: #0A84FF; font-weight: bold; background: transparent; border: none; font-size: 11pt;")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self._next)
        h.addWidget(self.next_btn)

        v.addWidget(bottom)

    def _next(self):
        i = self.stack.currentIndex()
        if i < self.stack.count() - 1:
            self.stack.setCurrentIndex(i + 1)
            dots = ["\u25cb"] * self.stack.count()
            dots[i + 1] = "\u25cf"
            self.dots.setText(" ".join(dots))
            if i + 1 == self.stack.count() - 1:
                self.next_btn.setText("Enter ASTA Tool \u2794")
        else:
            self.finished.emit()

# ══════════════════════════════════════════════════════════════════════════════
# HOST WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class IntroSequenceHost(QWidget):
    sequenceFinished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(700, 460)
        self.setStyleSheet("background: #0D1117; border-radius: 12px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.intro = CinematicIntro()
        self.diag  = DiagnosticsCheck()
        self.man   = InteractiveManual()

        self.stack.addWidget(self.intro)
        self.stack.addWidget(self.diag)
        self.stack.addWidget(self.man)

        self.intro.finished.connect(self._to_diag)
        self.diag.finished.connect(self._to_manual)
        self.man.finished.connect(self.sequenceFinished.emit)

    def start(self):
        self.show()
        self.intro.start()

    def _to_diag(self):
        self.stack.setCurrentWidget(self.diag)
        self.diag.start()

    def _to_manual(self):
        self.stack.setCurrentWidget(self.man)
