"""
HandiAI — Main Window
QMainWindow with sidebar + topbar + QStackedWidget pages.
"""

import sys
import os

# ── Ensure project root is on sys.path ──────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QStackedWidget, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase, QPalette, QColor

# ── UI components ────────────────────────────────────────────
from ui.sidebar import Sidebar
from ui.topbar  import TopBar

# ── Pages ────────────────────────────────────────────────────
from pages.dashboard     import DashboardPage
from pages.upload        import UploadPage
from pages.models        import ModelsPage
from pages.explainability import ExplainabilityPage
from pages.monitoring    import MonitoringPage
from pages.logs          import ProductionLogsPage

from engine import DataEngine


# ─────────────────────────────────────────────────────────────
#  Theme loader
# ─────────────────────────────────────────────────────────────
def load_stylesheet():
    qss_path = os.path.join(ROOT, "styles", "theme.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# ─────────────────────────────────────────────────────────────
#  Main Window
# ─────────────────────────────────────────────────────────────
class HandiAIMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HandiAI — Explainable AI Platform")
        self.setMinimumSize(1280, 800)
        self.resize(1440, 900)
        self._setup_ui()

    def _setup_ui(self):
        # Central widget
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root_lay = QHBoxLayout(central)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────
        self._sidebar = Sidebar()
        self._sidebar.page_changed.connect(self._switch_page)
        root_lay.addWidget(self._sidebar)

        # ── Right panel (topbar + pages) ─────────────────────
        right = QWidget()
        right.setObjectName("centralWidget")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)

        self._topbar = TopBar()
        self._topbar.page_requested.connect(self._switch_page)
        right_lay.addWidget(self._topbar)

        # ── Live Data Engine ─────────────────────────────────
        self.engine = DataEngine()

        # ── Stacked pages ────────────────────────────────────
        self._stack = QStackedWidget()
        self._stack.setObjectName("centralWidget")

        self._pages = [
            DashboardPage(self.engine, navigate_fn=self._switch_page),  # 0
            UploadPage(self.engine),                                     # 1
            ModelsPage(self.engine, navigate_fn=self._switch_page),      # 2
            ExplainabilityPage(self.engine),                             # 3
            MonitoringPage(self.engine),                                 # 4
            ProductionLogsPage(self.engine),                             # 5
        ]
        for page in self._pages:
            self._stack.addWidget(page)

        right_lay.addWidget(self._stack, 1)
        root_lay.addWidget(right, 1)

        # Start the live data engine
        self.engine.start()

    _PAGE_TITLES = [
        "Dashboard", "Upload & Analyze", "Models",
        "Explainability", "Monitoring", "Production Logs",
    ]

    def _switch_page(self, index: int):
        self._stack.setCurrentIndex(index)
        self._sidebar._select(index)
        self._topbar.set_title(self._PAGE_TITLES[index])


# ─────────────────────────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────────────────────────
def main():
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("HandiAI")
    app.setOrganizationName("HandiAI Labs")
    app.setStyle("Fusion")

    # Dark palette base (QSS overrides most of it)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor("#111111"))
    palette.setColor(QPalette.ColorRole.Base,            QColor("#f8f8f8"))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#f2f2f2"))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor("#f8f8f8"))
    palette.setColor(QPalette.ColorRole.ToolTipText,     QColor("#333333"))
    palette.setColor(QPalette.ColorRole.Text,            QColor("#111111"))
    palette.setColor(QPalette.ColorRole.Button,          QColor("#f0f0f0"))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor("#111111"))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor("#111111"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    # Load stylesheet
    app.setStyleSheet(load_stylesheet())

    # Global font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = HandiAIMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
