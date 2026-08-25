# -*- coding: utf-8 -*-
"""
ASTA Tool – Image Thumbnail Widget
Clickable thumbnail that opens the full image in the OS default viewer.
"""

import os
import subprocess
import sys

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui  import QPixmap, QCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy


class ThumbnailWidget(QWidget):
    """A single clickable image card with filename label beneath it."""

    def __init__(self, image_path: str, thumb_size: int = 180, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.thumb_size = thumb_size

        self.setFixedSize(thumb_size + 16, thumb_size + 44)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setToolTip(f"Open: {os.path.basename(image_path)}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # ── Image label ─────────────────────────────────────────────────────
        self.img_label = QLabel()
        self.img_label.setFixedSize(thumb_size, thumb_size)
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setScaledContents(False)
        self._load_pixmap()

        # ── Filename label ───────────────────────────────────────────────────
        name = os.path.basename(image_path)
        if len(name) > 24:
            name = name[:21] + "..."
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setObjectName("sectionLabel")
        self.name_label.setWordWrap(False)
        self.name_label.setFixedWidth(thumb_size)

        layout.addWidget(self.img_label)
        layout.addWidget(self.name_label)

        self._apply_card_style()

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _load_pixmap(self):
        px = QPixmap(self.image_path)
        if px.isNull():
            self.img_label.setText("⚠ No preview")
        else:
            scaled = px.scaled(
                self.thumb_size, self.thumb_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.img_label.setPixmap(scaled)

    def _apply_card_style(self):
        self.setStyleSheet("""
            ThumbnailWidget {
                border-radius: 8px;
                border: 1px solid transparent;
            }
            ThumbnailWidget:hover {
                border: 1px solid #3A8EBA;
                background-color: rgba(58, 142, 186, 0.08);
            }
        """)

    # ── Mouse events ───────────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._open_image()
        super().mousePressEvent(event)

    def _open_image(self):
        try:
            if sys.platform.startswith("win"):
                os.startfile(self.image_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.image_path])
            else:
                subprocess.Popen(["xdg-open", self.image_path])
        except Exception as e:
            print(f"Could not open image: {e}")
