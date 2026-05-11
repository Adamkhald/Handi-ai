"""
HandiAI — Top Bar
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Signal


class TopBar(QWidget):
    page_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setFixedHeight(56)
        self.setStyleSheet(
            "QWidget#topbar { background: #ffffff; border-bottom: 1px solid #e8e8e8; }"
        )
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 0, 28, 0)
        layout.setSpacing(0)

        self._title = QLabel("Dashboard")
        self._title.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #111111; background: transparent;"
        )
        layout.addWidget(self._title)
        layout.addStretch()

    def set_title(self, title: str):
        self._title.setText(title)
