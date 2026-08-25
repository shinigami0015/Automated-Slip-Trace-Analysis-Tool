# -*- coding: utf-8 -*-
"""
ASTA Tool -- Premium Animated Splash Screen
Adobe / Apple-style launch experience.
"""
import math

from PyQt6.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve,
                           pyqtProperty, QPointF)
from PyQt6.QtGui import (QPainter, QColor, QLinearGradient, QRadialGradient,
                          QPen, QBrush, QFont, QPolygonF)
from PyQt6.QtWidgets import QWidget, QApplication


class SplashScreen(QWidget):
    """
    Frameless animated splash with:
      - Glowing hexagonal crystal lattice logo (QPainter)
      - Rotating orbital particle
      - Thin animated progress strip with tip glow
      - Fade-in / fade-out QPropertyAnimation
    """

    W = 700
    H = 420

    MESSAGES = [
        "Initializing environment...",
        "Loading crystallographic models...",
        "Preparing EBSD pipeline...",
        "Configuring slip systems...",
        "Setting up Schmid analysis...",
        "Almost ready...",
        "Welcome.",
    ]

    def __init__(self):
        super().__init__()
        self._progress  = 0.0
        self._dot_angle = 0.0
        self._msg_idx   = 0
        self._setup_window()
        self._setup_animations()

    # ── Window setup ───────────────────────────────────────────────────────────
    def _setup_window(self):
        self.setFixedSize(self.W, self.H)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width()  - self.W) // 2,
            (screen.height() - self.H) // 2,
        )

    # ── Animations ─────────────────────────────────────────────────────────────
    def _setup_animations(self):
        # Fade-in animation (window opacity 0 -> 1)
        self._fade_in = QPropertyAnimation(self, b"opacityProp")
        self._fade_in.setDuration(700)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Progress fill animation (0.0 -> 1.0 over 2.8 s)
        self._prog_anim = QPropertyAnimation(self, b"progressProp")
        self._prog_anim.setDuration(2800)
        self._prog_anim.setStartValue(0.0)
        self._prog_anim.setEndValue(1.0)
        self._prog_anim.setEasingCurve(QEasingCurve.Type.InOutSine)

        # 60fps render tick for particle rotation
        self._tick = QTimer(self)
        self._tick.setInterval(16)
        self._tick.timeout.connect(self._on_tick)

    # ── Qt Properties (required by QPropertyAnimation) ─────────────────────────
    def _get_opacity(self): return self.windowOpacity()
    def _set_opacity(self, v): self.setWindowOpacity(v)
    opacityProp = pyqtProperty(float, _get_opacity, _set_opacity)

    def _get_progress(self): return self._progress
    def _set_progress(self, v):
        self._progress = v
        self._msg_idx  = min(
            int(v * len(self.MESSAGES)),
            len(self.MESSAGES) - 1
        )
        self.update()
    progressProp = pyqtProperty(float, _get_progress, _set_progress)

    # ── Public API ─────────────────────────────────────────────────────────────
    def start_animation(self):
        self._tick.start()
        self._fade_in.start()
        self._prog_anim.start()

    def fade_out(self, callback=None):
        self._tick.stop()
        anim = QPropertyAnimation(self, b"opacityProp")
        anim.setDuration(450)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        if callback:
            anim.finished.connect(callback)
        anim.finished.connect(self.close)
        anim.start()
        self._fade_out_ref = anim  # keep alive

    # ── Tick ───────────────────────────────────────────────────────────────────
    def _on_tick(self):
        self._dot_angle = (self._dot_angle + 2.2) % 360.0
        self.update()

    # ══════════════════════════════════════════════════════════════════════════
    # PAINT
    # ══════════════════════════════════════════════════════════════════════════
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        W, H = self.W, self.H

        # ── Background ─────────────────────────────────────────────────────────
        bg = QLinearGradient(0, 0, 0, H)
        bg.setColorAt(0.0, QColor("#1E1E22"))
        bg.setColorAt(1.0, QColor("#111114"))
        p.setBrush(QBrush(bg))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, W, H, 16, 16)

        # ── Top accent stripe ──────────────────────────────────────────────────
        stripe = QLinearGradient(0, 0, W, 0)
        stripe.setColorAt(0.00, QColor(0, 0, 0, 0))
        stripe.setColorAt(0.30, QColor("#0A84FF"))
        stripe.setColorAt(0.70, QColor("#409CFF"))
        stripe.setColorAt(1.00, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(stripe))
        p.drawRoundedRect(0, 0, W, 3, 2, 2)

        # ── Crystal logo ────────────────────────────────────────────────────────
        cx, cy = W // 2, 150
        self._paint_crystal(p, cx, cy, 64)

        # ── "ASTA Tool" ──────────────────────────────────────────────────────────
        tf = QFont("Segoe UI", 28, QFont.Weight.Light)
        tf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 10)
        p.setFont(tf)
        p.setPen(QColor("#F5F5F7"))
        p.drawText(0, cy + 84, W, 48,
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                   "ASTA Tool")

        # ── Subtitle ────────────────────────────────────────────────────────────
        sf = QFont("Segoe UI", 8, QFont.Weight.Normal)
        sf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 3.5)
        p.setFont(sf)
        p.setPen(QColor("#48484A"))
        p.drawText(0, cy + 136, W, 20,
                   Qt.AlignmentFlag.AlignHCenter,
                   "SLIP TRACE  \u00b7  SCHMID FACTOR ANALYSIS")

        # ── Progress bar ────────────────────────────────────────────────────────
        BX = 110; BY = H - 70; BW = W - 220; BH = 2
        # Track
        p.setBrush(QColor("#2C2C2E"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(BX, BY, BW, BH, 1, 1)
        # Fill
        fill_w = int(BW * self._progress)
        if fill_w > 4:
            fg = QLinearGradient(BX, 0, BX + BW, 0)
            fg.setColorAt(0.0, QColor("#0071E3"))
            fg.setColorAt(1.0, QColor("#409CFF"))
            p.setBrush(QBrush(fg))
            p.drawRoundedRect(BX, BY, fill_w, BH, 1, 1)
            # Glowing tip
            tx = BX + fill_w
            tg = QRadialGradient(tx, BY + 1, 10)
            tg.setColorAt(0.0, QColor(64, 156, 255, 180))
            tg.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(tg))
            p.drawEllipse(tx - 10, BY - 9, 20, 20)

        # ── Status message ──────────────────────────────────────────────────────
        msg  = self.MESSAGES[self._msg_idx]
        mf   = QFont("Segoe UI", 8)
        p.setFont(mf)
        p.setPen(QColor("#3A3A3C"))
        p.drawText(0, BY + 14, W, 20, Qt.AlignmentFlag.AlignHCenter, msg)

        # ── Bottom branding ─────────────────────────────────────────────────────
        bf = QFont("Segoe UI", 7)
        p.setFont(bf)
        p.setPen(QColor("#2A2A2C"))
        p.drawText(W - 110, H - 18, 100, 14,
                   Qt.AlignmentFlag.AlignRight,
                   "IISc Materials Lab  \u00b7  v1.0.0")

        p.end()

    # ── Crystal Lattice Logo ───────────────────────────────────────────────────
    def _paint_crystal(self, p: QPainter, cx: int, cy: int, r: float):
        def pts(radius):
            return [
                QPointF(cx + radius * math.cos(math.radians(60 * k - 30)),
                        cy + radius * math.sin(math.radians(60 * k - 30)))
                for k in range(6)
            ]

        # Ambient glow
        ag = QRadialGradient(cx, cy, r * 2.2)
        ag.setColorAt(0.0, QColor(10, 132, 255, 40))
        ag.setColorAt(1.0, QColor(0,  0,   0,   0))
        p.setBrush(QBrush(ag))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(cx - r*2.2), int(cy - r*2.2), int(r*4.4), int(r*4.4))

        # Three concentric hexagons
        for radius, alpha, width in [
            (r,        200, 1.5),
            (r * 0.60, 140, 1.0),
            (r * 0.28,  80, 0.8),
        ]:
            p.setPen(QPen(QColor(10, 132, 255, alpha), width))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolygon(QPolygonF(pts(radius)))

        # Lattice spokes
        outer = pts(r)
        inner = pts(r * 0.60)
        p.setPen(QPen(QColor(64, 156, 255, 65), 0.8))
        for k in range(6):
            p.drawLine(outer[k], inner[k])
            p.drawLine(inner[k], QPointF(cx, cy))

        # Rotating orbital particle
        angle_rad = math.radians(self._dot_angle - 30)
        px_  = cx + r * math.cos(angle_rad)
        py_  = cy + r * math.sin(angle_rad)
        dg   = QRadialGradient(px_, py_, 12)
        dg.setColorAt(0.0, QColor(64, 156, 255, 210))
        dg.setColorAt(1.0, QColor(0,   0,   0,    0))
        p.setBrush(QBrush(dg))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(px_ - 12), int(py_ - 12), 24, 24)
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(int(px_ - 3), int(py_ - 3), 6, 6)

        # Center core glow
        cg = QRadialGradient(cx, cy, 16)
        cg.setColorAt(0.0, QColor(64, 156, 255, 230))
        cg.setColorAt(0.5, QColor(10, 132, 255, 100))
        cg.setColorAt(1.0, QColor(0,   0,   0,    0))
        p.setBrush(QBrush(cg))
        p.drawEllipse(cx - 16, cy - 16, 32, 32)
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(cx - 3, cy - 3, 6, 6)
