"""
HandiAI — Datasets Page
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt

import data
from widgets.components import Card, add_shadow


class DatasetsPage(QWidget):
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
        ph = QHBoxLayout()
        col = QVBoxLayout(); col.setSpacing(2)
        t = QLabel("Datasets")
        t.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; background: transparent;")
        s = QLabel("Manage training, test, and reference datasets")
        s.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        col.addWidget(t); col.addWidget(s)
        ph.addLayout(col); ph.addStretch()

        btn = QPushButton("+ Upload Dataset")
        btn.setObjectName("btn_primary")
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ph.addWidget(btn)
        lay.addLayout(ph)

        if not data.DATASETS:
            empty_card = Card(); add_shadow(empty_card)
            el = QVBoxLayout(empty_card); el.setContentsMargins(24, 32, 24, 32)
            empty_lbl = QLabel("No datasets loaded yet.\nUpload a CSV on the Upload & Analyze page to get started.")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("font-size: 13px; color: #5a5888; background: transparent;")
            el.addWidget(empty_lbl)
            lay.addWidget(empty_card)
        else:
            summary_row = QHBoxLayout(); summary_row.setSpacing(14)
            for title, val, color in [
                ("Total Datasets", str(len(data.DATASETS)), "#00e0b8"),
                ("Total Records",  "—",                     "#b46cff"),
                ("Storage Used",   "—",                     "#ffd400"),
                ("Data Types",     "—",                     "#4d9fff"),
            ]:
                card = Card(); card.setMinimumHeight(80); add_shadow(card)
                cl = QVBoxLayout(card); cl.setContentsMargins(16, 12, 16, 12); cl.setSpacing(3)
                vl = QLabel(val)
                vl.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {color}; background: transparent;")
                nl = QLabel(title)
                nl.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
                cl.addWidget(vl); cl.addWidget(nl)
                summary_row.addWidget(card)
            lay.addLayout(summary_row)

            TYPE_COLORS = {"Tabular": "#00e0b8", "Text": "#b46cff", "Image": "#ffd400"}
            TYPE_ICONS  = {"Tabular": "📊",       "Text": "📝",      "Image": "🖼"}
            grid_widget = QWidget(); grid_widget.setStyleSheet("background: transparent;")
            grid_lay = QVBoxLayout(grid_widget); grid_lay.setContentsMargins(0, 0, 0, 0); grid_lay.setSpacing(12)

            for dataset in data.DATASETS:
                card = Card(); add_shadow(card)
                cl = QHBoxLayout(card); cl.setContentsMargins(18, 14, 18, 14); cl.setSpacing(16)
                dtype = dataset["type"]; color = TYPE_COLORS.get(dtype, "#9896c8")
                icon_box = QWidget(); icon_box.setFixedSize(46, 46)
                icon_box.setStyleSheet(f"background: {color}22; border-radius: 10px; border: 1px solid {color}44;")
                ib_lay = QVBoxLayout(icon_box); ib_lay.setContentsMargins(0, 0, 0, 0)
                ic = QLabel(TYPE_ICONS.get(dtype, "📁"))
                ic.setStyleSheet("font-size: 20px; background: transparent;")
                ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
                ib_lay.addWidget(ic); cl.addWidget(icon_box)
                info = QVBoxLayout(); info.setSpacing(3)
                nm = QLabel(dataset["name"])
                nm.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
                meta = QLabel(f"{dataset['rows']:,} rows  ·  {dataset['cols']} features  ·  {dataset['size']}")
                meta.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
                info.addWidget(nm); info.addWidget(meta); cl.addLayout(info); cl.addStretch()
                tb = QLabel(dtype)
                tb.setStyleSheet(
                    f"background: {color}22; border: 1px solid {color}44; border-radius: 8px; "
                    f"color: {color}; font-size: 10px; font-weight: 700; padding: 2px 10px;"
                )
                cl.addWidget(tb)
                for icon, tip in [("🔍", "Preview"), ("📊", "Profile"), ("🗑", "Delete")]:
                    b = QPushButton(icon); b.setFixedSize(32, 32); b.setToolTip(tip)
                    b.setCursor(Qt.CursorShape.PointingHandCursor)
                    b.setStyleSheet(
                        "QPushButton { background: rgba(255,255,255,0.05); border: 1px solid #3a3670; "
                        "border-radius: 8px; font-size: 15px; }"
                        "QPushButton:hover { background: rgba(180,108,255,0.2); border: 1px solid #b46cff55; }"
                    )
                    cl.addWidget(b)
                grid_lay.addWidget(card)
            lay.addWidget(grid_widget)

        lay.addSpacing(10)
