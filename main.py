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
from pages.models        import ModelsPage
from pages.datasets      import DatasetsPage
from pages.explainability import ExplainabilityPage
from pages.monitoring    import MonitoringPage
from pages.drift         import DriftDetectionPage
from pages.metrics       import MetricsPage
from pages.logs          import ProductionLogsPage
from pages.reports       import ReportsPage
from pages.settings      import SettingsPage

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
        right_lay.addWidget(self._topbar)

        # ── Live Data Engine ─────────────────────────────────
        self.engine = DataEngine()

        # ── Stacked pages ────────────────────────────────────
        self._stack = QStackedWidget()
        self._stack.setObjectName("centralWidget")

        self._pages = [
            DashboardPage(self.engine),       # 0
            ModelsPage(),                     # 1 (No live data needed yet)
            DatasetsPage(),                   # 2
            ExplainabilityPage(self.engine),  # 3
            MonitoringPage(self.engine),      # 4
            DriftDetectionPage(self.engine),  # 5
            MetricsPage(),                    # 6
            ProductionLogsPage(self.engine),  # 7
            ReportsPage(),                    # 8
            SettingsPage(),                   # 9
        ]
        for page in self._pages:
            self._stack.addWidget(page)

        right_lay.addWidget(self._stack, 1)
        root_lay.addWidget(right, 1)

        # Start the engine
        self.engine.start()

    def _switch_page(self, index: int):
        self._stack.setCurrentIndex(index)


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
    palette.setColor(QPalette.ColorRole.Window,          QColor("#1d1b3a"))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor("#e0dff5"))
    palette.setColor(QPalette.ColorRole.Base,            QColor("#26234d"))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#2a2855"))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor("#26234d"))
    palette.setColor(QPalette.ColorRole.ToolTipText,     QColor("#e0dff5"))
    palette.setColor(QPalette.ColorRole.Text,            QColor("#e0dff5"))
    palette.setColor(QPalette.ColorRole.Button,          QColor("#26234d"))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor("#e0dff5"))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor("#b46cff"))
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
