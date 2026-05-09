"""
HandiAI — Left Sidebar Navigation
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath, QFont

from widgets.components import Card, make_label, add_shadow


NAV_ITEMS = [
    ("⊞", "Dashboard",       0),
    ("⬡", "Models",          1),
    ("⬢", "Datasets",        2),
    ("◎", "Explainability",  3),
    ("◈", "Monitoring",      4),
    ("⚑", "Drift Detection", 5),
    ("▣", "Metrics",         6),
    ("≡", "Production Logs", 7),
    ("⊞", "Reports",         8),
    ("⚙", "Settings",        9),
]


class NavButton(QPushButton):
    def __init__(self, icon, label, index, parent=None):
        super().__init__(parent)
        self._icon  = icon
        self._label = label
        self._index = index
        self._active = False
        self.setFixedHeight(42)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("nav_btn")
        self._update_style()

    def set_active(self, active: bool):
        self._active = active
        self._update_style()
        self.update()

    def _update_style(self):
        if self._active:
            self.setObjectName("nav_btn_active")
        else:
            self.setObjectName("nav_btn")
        self.setStyle(self.style())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        if self._active:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#b46cff30"))
            path = QPainterPath()
            path.addRoundedRect(3, 2, w - 6, h - 4, 10, 10)
            painter.drawPath(path)

            # Glowing left border
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0, QColor("#b46cff"))
            grad.setColorAt(1, QColor("#7c3aed"))
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(3, 6, 3, h - 12, 2, 2)

        elif self.underMouse():
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#b46cff18"))
            path = QPainterPath()
            path.addRoundedRect(3, 2, w - 6, h - 4, 10, 10)
            painter.drawPath(path)

        # Icon
        icon_color = QColor("#ffffff") if self._active else QColor("#9896c8")
        painter.setPen(icon_color)
        f_icon = QFont("Segoe UI", 13)
        painter.setFont(f_icon)
        painter.drawText(QRect(14, 0, 26, h), Qt.AlignmentFlag.AlignCenter, self._icon)

        # Label
        label_color = QColor("#ffffff") if self._active else QColor("#9896c8")
        painter.setPen(label_color)
        f_lbl = QFont("Segoe UI", 11, QFont.Weight.Bold if self._active else QFont.Weight.Normal)
        painter.setFont(f_lbl)
        painter.drawText(QRect(46, 0, w - 56, h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self._label)

        painter.end()




class AvatarWidget(QWidget):
    """Circular avatar drawn with initials."""

    def __init__(self, initials="AK", size=38, bg="#b46cff", parent=None):
        super().__init__(parent)
        self._initials = initials
        self._bg = QColor(bg)
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._bg)
        painter.drawEllipse(0, 0, self.width(), self.height())
        painter.setPen(QColor("#ffffff"))
        f = QFont("Segoe UI", 11, QFont.Weight.Bold)
        painter.setFont(f)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._initials)
        painter.end()


class Sidebar(QWidget):
    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(230)
        self._buttons: list[NavButton] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 16)
        layout.setSpacing(0)

        # ── Logo Section ──────────────────────────────────────
        logo_widget = QWidget()
        logo_widget.setObjectName("logo_section")
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(8, 4, 8, 4)
        logo_layout.setSpacing(10)

        # Logo icon (drawn as a neon circle)
        logo_icon = QWidget()
        logo_icon.setFixedSize(38, 38)
        logo_icon.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #b46cff, stop:1 #00e0b8);"
            "border-radius: 10px;"
        )
        logo_lbl = QLabel("H")
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet(
            "font-size: 18px; font-weight: 900; color: #1a1836; background: transparent;"
        )
        logo_il = QVBoxLayout(logo_icon)
        logo_il.setContentsMargins(0, 0, 0, 0)
        logo_il.addWidget(logo_lbl)

        logo_layout.addWidget(logo_icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title = QLabel("HandiAI")
        title.setStyleSheet(
            "font-size: 16px; font-weight: 800; color: #ffffff;"
            "letter-spacing: 1px; background: transparent;"
        )
        subtitle = QLabel("Explainable AI Platform")
        subtitle.setStyleSheet(
            "font-size: 9px; color: #9896c8; letter-spacing: 0.3px; background: transparent;"
        )
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        logo_layout.addLayout(title_col)
        logo_layout.addStretch()

        layout.addWidget(logo_widget)
        layout.addSpacing(20)

        # Divider
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #3a3670; max-height: 1px;")
        layout.addWidget(sep)
        layout.addSpacing(10)

        # ── Nav Items ─────────────────────────────────────────
        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet(
            "font-size: 9px; color: #5a5888; letter-spacing: 1.5px; "
            "font-weight: 700; padding-left: 14px; background: transparent;"
        )
        layout.addWidget(nav_label)
        layout.addSpacing(6)

        for icon, label, idx in NAV_ITEMS:
            btn = NavButton(icon, label, idx)
            btn.clicked.connect(lambda checked=False, i=idx: self._on_nav(i))
            self._buttons.append(btn)
            layout.addWidget(btn)
            layout.addSpacing(2)

        layout.addStretch()

        # Divider
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background: #3a3670; max-height: 1px;")
        layout.addWidget(sep2)
        layout.addSpacing(10)

        # ── User Profile ──────────────────────────────────────
        user_card = QWidget()
        user_card.setObjectName("user_card")
        user_card.setStyleSheet(
            "QWidget#user_card { background: rgba(255,255,255,0.05);"
            "border: 1px solid #3a3670; border-radius: 12px; }"
        )
        uc_lay = QHBoxLayout(user_card)
        uc_lay.setContentsMargins(10, 10, 10, 10)
        uc_lay.setSpacing(10)

        avatar = AvatarWidget("AK", 36)
        uc_lay.addWidget(avatar)

        user_info = QVBoxLayout()
        user_info.setSpacing(1)
        uname = QLabel("Adham K.")
        uname.setStyleSheet("font-size: 12px; font-weight: 700; color: #ffffff; background: transparent;")
        urole = QLabel("ML Engineer")
        urole.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
        user_info.addWidget(uname)
        user_info.addWidget(urole)
        uc_lay.addLayout(user_info)
        uc_lay.addStretch()

        # Online dot
        dot = QLabel("●")
        dot.setStyleSheet("color: #00c97d; font-size: 10px; background: transparent;")
        uc_lay.addWidget(dot)

        layout.addWidget(user_card)

        # Activate first
        self._select(0)

    def _on_nav(self, index: int):
        self._select(index)
        self.page_changed.emit(index)

    def _select(self, index: int):
        for btn in self._buttons:
            btn.set_active(btn._index == index)
