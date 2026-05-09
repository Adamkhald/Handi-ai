"""
HandiAI — Top Navigation Bar
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPainter, QFont, QPainterPath, QBrush, QPen

from ui.sidebar import AvatarWidget


class GlowDot(QWidget):
    """Animated glowing status dot."""

    def __init__(self, color="#00c97d", size=10, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedSize(size + 8, size + 8)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = 5
        cx, cy = self.width() // 2, self.height() // 2

        # Glow ring
        glow = QColor(self._color)
        glow.setAlpha(50)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(cx - r - 3, cy - r - 3, (r + 3) * 2, (r + 3) * 2)

        # Core dot
        painter.setBrush(self._color)
        painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)
        painter.end()


class TopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setFixedHeight(70)
        self.setStyleSheet(
            "QWidget#topbar { background: #1d1b3a; border-bottom: 1px solid #2e2b5f; }"
        )
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        # ── Search Bar ────────────────────────────────────────
        search_container = QWidget()
        search_container.setFixedWidth(340)
        search_container.setStyleSheet(
            "background: #26234d; border-radius: 20px; border: 1px solid #3a3670;"
        )
        sc_lay = QHBoxLayout(search_container)
        sc_lay.setContentsMargins(14, 0, 14, 0)
        sc_lay.setSpacing(8)

        search_icon = QLabel("⌕")
        search_icon.setStyleSheet("color: #6664a0; font-size: 16px; background: transparent;")
        sc_lay.addWidget(search_icon)

        search = QLineEdit()
        search.setObjectName("search_input")
        search.setPlaceholderText("Search models, metrics, datasets…")
        search.setStyleSheet(
            "QLineEdit { background: transparent; border: none; color: #e0dff5; font-size: 13px; }"
            "QLineEdit::placeholder { color: #5a5888; }"
        )
        sc_lay.addWidget(search)
        layout.addWidget(search_container)
        layout.addStretch()

        # ── Deployment Status ─────────────────────────────────
        status_widget = QWidget()
        status_widget.setStyleSheet(
            "background: rgba(0,201,125,0.1); border: 1px solid #00c97d44; border-radius: 18px;"
        )
        st_lay = QHBoxLayout(status_widget)
        st_lay.setContentsMargins(12, 6, 16, 6)
        st_lay.setSpacing(8)

        dot = GlowDot("#00c97d")
        st_lay.addWidget(dot)

        st_label = QLabel("Production Active")
        st_label.setStyleSheet("color: #00c97d; font-size: 12px; font-weight: 600; background: transparent;")
        st_lay.addWidget(st_label)

        layout.addWidget(status_widget)

        # ── Icon Buttons ──────────────────────────────────────
        for icon, tip in [("🔔", "Notifications"), ("⚙", "Settings")]:
            btn = QPushButton(icon)
            btn.setObjectName("btn_icon")
            btn.setFixedSize(40, 40)
            btn.setToolTip(tip)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                "QPushButton { background: #26234d; border: 1px solid #3a3670; "
                "border-radius: 12px; font-size: 16px; }"
                "QPushButton:hover { background: rgba(180,108,255,0.15); border: 1px solid #b46cff44; }"
            )

            # Notification badge
            if icon == "🔔":
                badge_container = QWidget()
                badge_container.setFixedSize(40, 40)
                bc_lay = QHBoxLayout(badge_container)
                bc_lay.setContentsMargins(0, 0, 0, 0)
                bc_lay.addWidget(btn)
                badge = QLabel("3")
                badge.setObjectName("badge")
                badge.setFixedSize(16, 16)
                badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                badge.setStyleSheet(
                    "background: #ff5577; border-radius: 8px; "
                    "color: white; font-size: 9px; font-weight: 700;"
                )
                badge.move(26, 4)
                badge.setParent(btn)
                layout.addWidget(btn)
            else:
                layout.addWidget(btn)

        # ── Avatar ────────────────────────────────────────────
        avatar = AvatarWidget("AK", 38)
        layout.addWidget(avatar)
