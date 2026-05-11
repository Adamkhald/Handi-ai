"""
HandiAI — Left Sidebar Navigation
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, Signal, QSize, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont

from widgets.components import add_shadow


NAV_ITEMS = [
    ("⊞", "Dashboard",        0),
    ("↑", "Upload & Analyze", 1),
    ("◉", "Models",           2),
    ("◎", "Explainability",   3),
    ("◈", "Monitoring",       4),
    ("≡", "Production Logs",  5),
]


class NavButton(QPushButton):
    def __init__(self, icon, label, index, parent=None):
        super().__init__(parent)
        self._icon   = icon
        self._label  = label
        self._index  = index
        self._active = False
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("nav_btn")

    def set_active(self, active: bool):
        self._active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        if self._active:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#111111"))
            path = QPainterPath()
            path.addRoundedRect(4, 2, w - 8, h - 4, 8, 8)
            painter.drawPath(path)
            icon_color  = QColor("#ffffff")
            label_color = QColor("#ffffff")
        elif self.underMouse():
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#ebebeb"))
            path = QPainterPath()
            path.addRoundedRect(4, 2, w - 8, h - 4, 8, 8)
            painter.drawPath(path)
            icon_color  = QColor("#333333")
            label_color = QColor("#333333")
        else:
            icon_color  = QColor("#888888")
            label_color = QColor("#888888")

        painter.setPen(icon_color)
        painter.setFont(QFont("Segoe UI", 12))
        painter.drawText(QRect(12, 0, 24, h), Qt.AlignmentFlag.AlignCenter, self._icon)

        painter.setPen(label_color)
        weight = QFont.Weight.Bold if self._active else QFont.Weight.Normal
        painter.setFont(QFont("Segoe UI", 11, weight))
        painter.drawText(
            QRect(44, 0, w - 52, h),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self._label,
        )
        painter.end()


class Sidebar(QWidget):
    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self._buttons: list[NavButton] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(0)

        # Logo
        logo_row = QHBoxLayout()
        logo_row.setContentsMargins(8, 4, 8, 4)
        logo_row.setSpacing(10)

        logo_icon = QWidget()
        logo_icon.setFixedSize(32, 32)
        logo_icon.setStyleSheet("background: #111111; border-radius: 7px;")
        logo_lbl = QLabel("H")
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet(
            "font-size: 15px; font-weight: 900; color: #ffffff; background: transparent;"
        )
        logo_il = QVBoxLayout(logo_icon)
        logo_il.setContentsMargins(0, 0, 0, 0)
        logo_il.addWidget(logo_lbl)
        logo_row.addWidget(logo_icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title = QLabel("HandiAI")
        title.setStyleSheet(
            "font-size: 14px; font-weight: 800; color: #111111; background: transparent;"
        )
        subtitle = QLabel("Explainable AI")
        subtitle.setStyleSheet(
            "font-size: 9px; color: #aaaaaa; background: transparent;"
        )
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        logo_row.addLayout(title_col)
        logo_row.addStretch()

        layout.addLayout(logo_row)
        layout.addSpacing(20)

        # Nav items
        for icon, label, idx in NAV_ITEMS:
            btn = NavButton(icon, label, idx)
            btn.clicked.connect(lambda checked=False, i=idx: self._on_nav(i))
            self._buttons.append(btn)
            layout.addWidget(btn)
            layout.addSpacing(1)

        layout.addStretch()
        self._select(0)

    def _on_nav(self, index: int):
        self._select(index)
        self.page_changed.emit(index)

    def _select(self, index: int):
        for btn in self._buttons:
            btn.set_active(btn._index == index)
