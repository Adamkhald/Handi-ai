"""
HandiAI — Models Page (Import / Upload)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QProgressBar, QGridLayout, QFileDialog,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QMimeData, QRect
from PySide6.QtGui import (
    QPainter, QColor, QPen, QFont, QPainterPath,
    QBrush, QDragEnterEvent, QDropEvent
)

import data
from widgets.components import Card, add_shadow


class DropZone(QWidget):
    """Drag-and-drop upload zone with dashed glowing border."""

    def __init__(self, label, formats, icon="📁", parent=None):
        super().__init__(parent)
        self._label    = label
        self._formats  = formats
        self._icon     = icon
        self._hover    = False
        self._filename = None
        self.setAcceptDrops(True)
        self.setMinimumHeight(130)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setObjectName("upload_zone")

    def mousePressEvent(self, event):
        dialog = QFileDialog(self)
        dialog.setNameFilter(f"Files ({' '.join(self._formats)})")
        if dialog.exec():
            files = dialog.selectedFiles()
            if files:
                self._filename = files[0].replace("\\", "/").split("/")[-1]
                self.update()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self._hover = True
            self.update()
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._hover = False
        self.update()

    def dropEvent(self, event: QDropEvent):
        self._hover = False
        urls = event.mimeData().urls()
        if urls:
            self._filename = urls[0].toLocalFile().replace("\\", "/").split("/")[-1]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        accent = QColor("#333333") if self._hover else QColor("#aaaaaa")
        bg     = QColor("#ebebeb") if self._hover else QColor("#f5f5f5")

        path = QPainterPath()
        path.addRoundedRect(2, 2, w - 4, h - 4, 14, 14)
        painter.fillPath(path, QBrush(bg))

        pen = QPen(accent, 2, Qt.PenStyle.DashLine)
        pen.setDashPattern([6, 4])
        painter.setPen(pen)
        painter.drawPath(path)

        # Icon
        painter.setPen(QColor("#555555"))
        painter.setFont(QFont("Segoe UI", 22))
        painter.drawText(QRect(0, 0, w, h // 2), Qt.AlignmentFlag.AlignCenter, self._icon)

        # Text
        if self._filename:
            painter.setPen(QColor("#cccccc"))
            painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            painter.drawText(
                QRect(0, h // 2, w, h // 2),
                Qt.AlignmentFlag.AlignCenter,
                f"✓  {self._filename}"
            )
        else:
            painter.setPen(QColor("#888888"))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(
                QRect(0, h // 2 - 10, w, 22),
                Qt.AlignmentFlag.AlignCenter,
                self._label
            )
            painter.setFont(QFont("Segoe UI", 9))
            painter.setPen(QColor("#444444"))
            painter.drawText(
                QRect(0, h // 2 + 14, w, 22),
                Qt.AlignmentFlag.AlignCenter,
                "  ".join(self._formats)
            )

        painter.end()


class ModelsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("page_container")
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        content = QWidget()
        content.setObjectName("page_container")
        scroll.setWidget(content)
        outer.addWidget(scroll)

        lay = QVBoxLayout(content)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(20)

        # Header
        pg_title = QLabel("Model Import")
        pg_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #000000; background: transparent;")
        pg_sub = QLabel("Upload model files, test datasets, and validation datasets")
        pg_sub.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
        lay.addWidget(pg_title)
        lay.addWidget(pg_sub)

        # ── Upload Zones Row ──────────────────────────────────
        upload_card = Card()
        add_shadow(upload_card)
        uc_lay = QVBoxLayout(upload_card)
        uc_lay.setContentsMargins(20, 18, 20, 18)
        uc_lay.setSpacing(14)

        uc_title = QLabel("Upload Files")
        uc_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #000000; background: transparent;")
        uc_lay.addWidget(uc_title)

        zones_row = QHBoxLayout()
        zones_row.setSpacing(16)

        for label, fmts, icon in [
            ("Drop Model File Here", ["*.pkl", "*.onnx", "*.pt", "*.h5"], "🧠"),
            ("Drop Test Dataset",    ["*.csv", "*.parquet", "*.json"],    "📊"),
            ("Drop Validation Set",  ["*.csv", "*.parquet"],               "✅"),
        ]:
            zone = DropZone(label, fmts, icon)
            zones_row.addWidget(zone)

        uc_lay.addLayout(zones_row)

        # Format badges
        fmt_row = QHBoxLayout()
        fmt_row.setSpacing(8)
        fmt_label = QLabel("Supported formats:")
        fmt_label.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
        fmt_row.addWidget(fmt_label)
        for fmt in [".pkl", ".onnx", ".pt", ".h5", ".csv", ".parquet"]:
            badge = QLabel(fmt)
            badge.setStyleSheet(
                "background: #f0f0f0; border: 1px solid #d8d8d8; "
                "border-radius: 6px; color: #333333; font-size: 11px; padding: 2px 8px;"
            )
            fmt_row.addWidget(badge)
        fmt_row.addStretch()
        uc_lay.addLayout(fmt_row)
        lay.addWidget(upload_card)


        # ── Loaded Models Table ───────────────────────────────
        models_card = Card()
        add_shadow(models_card)
        ml_lay = QVBoxLayout(models_card)
        ml_lay.setContentsMargins(20, 18, 20, 18)
        ml_lay.setSpacing(12)

        mh = QHBoxLayout()
        mt = QLabel("Loaded Models")
        mt.setStyleSheet("font-size: 14px; font-weight: 700; color: #000000; background: transparent;")
        mh.addWidget(mt)
        mh.addStretch()
        btn_new = QPushButton("+ Import New")
        btn_new.setObjectName("btn_primary")
        btn_new.setFixedHeight(32)
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        mh.addWidget(btn_new)
        ml_lay.addLayout(mh)

        if not data.MODELS:
            empty = QLabel("No models loaded yet — use Upload & Analyze to import your first model.")
            empty.setStyleSheet(
                "font-size: 12px; color: #444444; padding: 20px 0; background: transparent;"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ml_lay.addWidget(empty)
        else:
            STATUS_COLORS = {
                "Production": "#aaaaaa", "Staging": "#888888",
                "Testing": "#aaaaaa",   "Retired": "#888888",
            }
            for model in data.MODELS:
                row = QHBoxLayout(); row.setSpacing(12)

                sc  = STATUS_COLORS.get(model["status"], "#888888")
                dot = QLabel("●")
                dot.setStyleSheet(f"color: {sc}; font-size: 10px; background: transparent;")
                row.addWidget(dot)

                name = QLabel(model["name"])
                name.setStyleSheet("font-size: 12px; font-weight: 600; color: #000000; background: transparent;")
                row.addWidget(name, 2)

                t = QLabel(model["type"])
                t.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
                row.addWidget(t, 1)

                acc = QLabel(f"{model['accuracy']:.1f}%")
                acc.setStyleSheet("font-size: 11px; color: #222222; font-weight: 600; background: transparent;")
                row.addWidget(acc)

                st_badge = QLabel(model["status"])
                st_badge.setStyleSheet(
                    f"background: {sc}22; border: 1px solid {sc}44; border-radius: 8px; "
                    f"color: {sc}; font-size: 10px; font-weight: 700; padding: 2px 8px;"
                )
                row.addWidget(st_badge)

                for icon, tip in [("🔍", "Explain"), ("📊", "Metrics"), ("🗑", "Remove")]:
                    b = QPushButton(icon)
                    b.setFixedSize(30, 30); b.setToolTip(tip)
                    b.setCursor(Qt.CursorShape.PointingHandCursor)
                    b.setStyleSheet(
                        "QPushButton { background: #f5f5f5; border: 1px solid #d8d8d8; "
                        "border-radius: 8px; font-size: 14px; }"
                        "QPushButton:hover { background: #e8e8e8; border: 1px solid #cccccc; }"
                    )
                    row.addWidget(b)

                ml_lay.addLayout(row)
                sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
                sep.setStyleSheet("background: #e0e0e0; max-height: 1px;")
                ml_lay.addWidget(sep)

        lay.addWidget(models_card)
        lay.addSpacing(10)
