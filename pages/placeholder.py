"""
HandiAI — Placeholder page for pages not yet fully implemented
(Shared component for Reports-detail, etc.)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt


class PlaceholderPage(QWidget):
    def __init__(self, title="Coming Soon", subtitle="This page is under construction.", parent=None):
        super().__init__(parent)
        self.setObjectName("page_container")
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(10)

        icon = QLabel("🚧")
        icon.setStyleSheet("font-size: 52px; background: transparent;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(icon)

        t = QLabel(title)
        t.setStyleSheet(
            "font-size: 22px; font-weight: 800; color: #ffffff; background: transparent;"
        )
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(t)

        s = QLabel(subtitle)
        s.setStyleSheet("font-size: 13px; color: #9896c8; background: transparent;")
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(s)
