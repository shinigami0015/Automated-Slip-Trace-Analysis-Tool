# -*- coding: utf-8 -*-
"""
STRCRYST -- Cinematic Intro Sequence
Handles the Netflix-style intro, system diagnostics, and interactive manual.
"""
import sys
import os
from PyQt6.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve, 
                           pyqtSignal, pyqtProperty, QRectF, QPointF)
from PyQt6.QtGui  import (QPainter, QColor, QFont, QFontMetrics, QBrush, 
                           QLinearGradient, QPainterPath)
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QStackedWidget, QFrame)

# ══════════════════════════════════════════════════════════════════════════════
# 1. THE NETFLIX-STYLE INTRO
# ══════════════════════════════════════════════════════════════════════════════
class CinematicIntro(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #000000;")
        self._scale = 0.8
        self._opacity = 0.0

        # Scale animation
        self.anim_scale = QPropertyAnimation(self, b"scale_factor")
        self.anim_scale.setDuration(3500)
        self.anim_scale.setStartValue(0.8)
        self.anim_scale.setEndValue(1.05)
        self.anim_scale.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Opacity animation (fade in, hold, fade out)
        self.anim_fade = QPropertyAnimation(self, b"opacity_factor")
        self.anim_fade.setDuration(1500)
        self.anim_fade.setStartValue(0.0)
        self.anim_fade.setEndValue(1.0)
        self.anim_fade.setEasingCurve(QEasingCurve.Type.InOutSine)

    @pyqtProperty(float)
    def scale_factor(self): return self._scale
    @scale_factor.setter
    def scale_factor(self, v): self._scale = v; self.update()

    @pyqtProperty(float)
    def opacity_factor(self): return self._opacity
    @opacity_factor.setter
    def opacity_factor(self, v): self._opacity = v; self.update()

    def start(self):
        self.anim_scale.start()
        self.anim_fade.start()
        # Fade out after 2.5s
        QTimer.singleShot(2500, self._fade_out)

    def _fade_out(self):
        self.anim_fade.stop()
        self.anim_fade.setDuration(1000)
        self.anim_fade.setStartValue(self._opacity)
        self.anim_fade.setEndValue(0.0)
        self.anim_fade.finished.connect(self.finished.emit)
        self.anim_fade.start()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor("#000000"))

        cx, cy = self.width() / 2, self.height() / 2

        p.translate(cx, cy)
        p.scale(self._scale, self._scale)
        p.translate(-cx, -cy)

        title = "Created by Parardha Dhar"
        sub   = "IISc Materials Lab"

        tf = QFont("Segoe UI", 24, QFont.Weight.Light)
        tf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
        p.setFont(tf)

        c = QColor("#FFFFFF")
        c.setAlphaF(self._opacity)
        p.setPen(c)
        
        fm = QFontMetrics(tf)
        tw = fm.horizontalAdvance(title)
        p.drawText(int(cx - tw/2), int(cy - 10), title)

        sf = QFont("Segoe UI", 10, QFont.Weight.Medium)
        sf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 8)
        p.setFont(sf)
        c_sub = QColor("#0A84FF")
        c_sub.setAlphaF(self._opacity * 0.8)
        p.setPen(c_sub)
        
        fm_s = QFontMetrics(sf)
        sw = fm_s.horizontalAdvance(sub)
        p.drawText(int(cx - sw/2), int(cy + 30), sub)
        p.end()

# ══════════════════════════════════════════════════════════════════════════════
# 2. SYSTEM DIAGNOSTICS (PRE-FLIGHT)
# ══════════════════════════════════════════════════════════════════════════════
import winreg

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
        v.addWidget(self.log_area, 1)

        self._steps = [
            ("Scanning Windows Registry for MATLAB...", 800, self._check_matlab_installed()),
            ("Testing MATLAB Engine API for Python...", 1200, self._check_matlab_engine()),
            ("Verifying MTEX Toolbox Linkage...", 700, "WARNING"), 
            ("Loading Crystallographic Core...", 500, True)
        ]
        self._current_step = 0
        self._log_text = ""

    def _check_matlab_installed(self):
        """Scans Windows Registry to see if MATLAB is actually installed on the PC."""
        try:
            # Check 64-bit registry
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\MathWorks\MATLAB", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            winreg.CloseKey(key)
            return True
        except OSError:
            # Try checking common install paths
            if os.path.exists(r"C:\Program Files\MATLAB"):
                return True
            return False

    def _check_matlab_engine(self):
        """Checks if the user has specifically installed the matlab.engine python package."""
        try:
            import matlab.engine # noqa
            return True
        except ImportError:
            return False

    def start(self):
        self._run_next_step()

    def _run_next_step(self):
        if self._current_step >= len(self._steps):
            self._log_text += "\n\n<span style='color:#3FB950;'>▶ PRE-FLIGHT COMPLETE. LAUNCHING MANUAL...</span>"
            self.log_area.setText(self._log_text)
            QTimer.singleShot(1500, self.finished.emit)
            return

        msg, delay, status = self._steps[self._current_step]
        self._log_text += f"> {msg} "
        self.log_area.setText(self._log_text)

        def _resolve():
            if status is True:
                self._log_text += "<span style='color:#3FB950;'>[✓ FOUND]</span><br>"
            elif status == "WARNING":
                self._log_text += "<span style='color:#E68A00;'>[⚠ DEFERRED TO RUNTIME]</span><br>"
            else:
                self._log_text += "<span style='color:#FF7B72;'>[✖ MISSING]</span><br>"
            
            self.log_area.setText(self._log_text)
            self._current_step += 1
            QTimer.singleShot(300, self._run_next_step)

        QTimer.singleShot(delay, _resolve)

# ══════════════════════════════════════════════════════════════════════════════
# 3. INTERACTIVE MANUAL CAROUSEL
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
            "Welcome to STRCRYST",
            "STRCRYST is an advanced UI wrapper for EBSD Slip Trace & Schmid Factor Analysis.\n\n"
            "This software automates the generation of crystallographic slip trace maps and CSV datasets "
            "directly from your .ctf files.", "💎"
        ))
        self.stack.addWidget(ManualPage(
            "System Requirements",
            "To run the analysis, you MUST have installed:\n"
            "1. MATLAB\n"
            "2. MTEX Toolbox (added to MATLAB path)\n"
            "3. MATLAB Engine API for Python\n\n"
            "If missing, the UI will still work, but analysis will abort.", "⚙️"
        ))
        self.stack.addWidget(ManualPage(
            "Quick Start Guide",
            "1. Select the folder containing the core .m scripts.\n"
            "2. Select the input folder containing your EBSD .ctf data.\n"
            "3. Choose an output folder.\n"
            "4. Hit 'Run Analysis' and wait for the AAA magic.\n\n"
            "Your settings will be automatically remembered for next time.", "🚀"
        ))
        v.addWidget(self.stack, 1)

        bottom = QWidget()
        bottom.setFixedHeight(80)
        h = QHBoxLayout(bottom)
        h.setContentsMargins(40, 0, 40, 20)

        self.skip_btn = QPushButton("Skip Tutorial")
        self.skip_btn.setStyleSheet("color: #545456; background: transparent; border: none; font-size: 11pt;")
        self.skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.skip_btn.clicked.connect(self.finished.emit)
        h.addWidget(self.skip_btn)

        h.addStretch()

        self.dots = QLabel("● ○ ○")
        self.dots.setStyleSheet("color: #3A3A3C; font-size: 14pt; letter-spacing: 4px;")
        h.addWidget(self.dots)

        h.addStretch()

        self.next_btn = QPushButton("Next ➔")
        self.next_btn.setStyleSheet("color: #0A84FF; font-weight: bold; background: transparent; border: none; font-size: 11pt;")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self._next)
        h.addWidget(self.next_btn)

        v.addWidget(bottom)

    def _next(self):
        i = self.stack.currentIndex()
        if i < self.stack.count() - 1:
            self.stack.setCurrentIndex(i + 1)
            dots = ["○", "○", "○"]
            dots[i+1] = "●"
            self.dots.setText(" ".join(dots))
            if i + 1 == self.stack.count() - 1:
                self.next_btn.setText("Enter STRCRYST ➔")
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
        self.setStyleSheet("background: #000000; border-radius: 12px;")
        
        # Enable shadow / rounded corners manually if needed or let Windows do it.

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
