# -*- coding: utf-8 -*-
"""
ASTA Tool -- Custom Frameless Title Bar
Standard Windows-style controls.
"""
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QEvent
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication


class _WinCtrlBtn(QWidget):
    """A single Windows-style control button (Minimize, Maximize, Close)."""

    clicked = pyqtSignal()

    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self._kind    = kind
        self._hovered = False
        self._pressed = False
        self.setFixedSize(46, 32)
        self.is_dark_mode = True

    def set_theme(self, is_dark: bool):
        self.is_dark_mode = is_dark
        self.update()

    def enterEvent(self, e):
        self._hovered = True
        self.update()

    def leaveEvent(self, e):
        self._hovered = False
        self._pressed = False
        self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self._hovered:
            self._pressed = False
            self.update()
            self.clicked.emit()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False) # crisp lines
        W, H = self.width(), self.height()

        # Background
        if self._hovered:
            if self._kind == "close":
                p.fillRect(0, 0, W, H, QColor("#E81123"))
            else:
                alpha = 40 if self.is_dark_mode else 25
                p.fillRect(0, 0, W, H, QColor(255, 255, 255, alpha) if self.is_dark_mode else QColor(0, 0, 0, alpha))
                if self._pressed:
                    alpha = 60 if self.is_dark_mode else 40
                    p.fillRect(0, 0, W, H, QColor(255, 255, 255, alpha) if self.is_dark_mode else QColor(0, 0, 0, alpha))

        # Icon color
        if self._kind == "close" and self._hovered:
            icon_col = QColor(255, 255, 255)
        else:
            icon_col = QColor("#F5F5F7") if self.is_dark_mode else QColor("#111111")
            
        p.setPen(QPen(icon_col, 1.0))
        cx, cy = W // 2, H // 2

        if self._kind == "min":
            p.drawLine(cx - 5, cy, cx + 5, cy)
        elif self._kind == "max":
            is_max = self.window().isMaximized() if self.window() else False
            if is_max:
                p.drawRect(cx - 4, cy - 2, 8, 8)
                p.drawLine(cx - 2, cy - 4, cx + 6, cy - 4)
                p.drawLine(cx + 6, cy - 4, cx + 6, cy - 2)
                p.drawLine(cx - 2, cy - 4, cx - 2, cy - 2)
            else:
                p.drawRect(cx - 5, cy - 5, 10, 10)
        elif self._kind == "close":
            p.drawLine(cx - 5, cy - 5, cx + 5, cy + 5)
            p.drawLine(cx - 5, cy + 5, cx + 5, cy - 5)

        p.end()


class TitleBar(QWidget):
    """
    Custom frameless-window title bar.
    Handles window dragging + double-click maximise.
    """
    closeRequested    = pyqtSignal()
    minimizeRequested = pyqtSignal()
    maximizeRequested = pyqtSignal()

    H = 32

    def __init__(self, title: str = "ASTA Tool", parent=None):
        super().__init__(parent)
        self.setFixedHeight(self.H)
        self.setObjectName("titleBar")
        self._drag_pos   = QPoint()
        self._dragging   = False
        self.is_dark_mode = True

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 0, 0)
        layout.setSpacing(0)

        # Left label
        self.lbl = QLabel(title)
        self.lbl.setStyleSheet("color: #8E8E93; font-family: 'Segoe UI'; font-size: 9pt; font-weight: 600; letter-spacing: 1px;")
        layout.addWidget(self.lbl)
        layout.addStretch()

        # Windows controls
        self._min_btn   = _WinCtrlBtn("min")
        self._max_btn   = _WinCtrlBtn("max")
        self._close_btn = _WinCtrlBtn("close")

        self._min_btn.clicked.connect(self.minimizeRequested)
        self._max_btn.clicked.connect(self.maximizeRequested)
        self._close_btn.clicked.connect(self.closeRequested)

        layout.addWidget(self._min_btn)
        layout.addWidget(self._max_btn)
        layout.addWidget(self._close_btn)
        
        # Install event filter to detect state changes for maximize icon
        if self.parent():
            self.parent().installEventFilter(self)

    def set_theme(self, is_dark: bool):
        self.is_dark_mode = is_dark
        col = "#8E8E93" if is_dark else "#545456"
        self.lbl.setStyleSheet(f"color: {col}; font-family: 'Segoe UI'; font-size: 9pt; font-weight: 600; letter-spacing: 1px;")
        self._min_btn.set_theme(is_dark)
        self._max_btn.set_theme(is_dark)
        self._close_btn.set_theme(is_dark)
        self.update()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self._max_btn.update()
        return super().eventFilter(obj, event)

    def paintEvent(self, _):
        p = QPainter(self)
        bg = QColor("#111114") if self.is_dark_mode else QColor("#E5E5E5")
        p.fillRect(self.rect(), bg)
        p.end()

    # ── Drag to move ───────────────────────────────────────────────────────────
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_pos = (e.globalPosition().toPoint()
                              - self.window().frameGeometry().topLeft())
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._dragging and (e.buttons() & Qt.MouseButton.LeftButton):
            win = self.window()
            if win.isMaximized():
                win.showNormal()
                # Adjust drag pos so it doesn't jump wildly
                self._drag_pos = QPoint(win.width() // 2, self.H // 2)
            win.move(e.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        self._dragging = False
        super().mouseReleaseEvent(e)

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.maximizeRequested.emit()
        super().mouseDoubleClickEvent(e)
