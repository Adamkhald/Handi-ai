"""
HandiAI — Reports Page
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import data
from widgets.components import Card, add_shadow


REPORTS = [
    {
        "title":    "Monthly Model Performance Report",
        "date":     "May 2026",
        "model":    "fraud_detector_v3",
        "status":   "Ready",
        "pages":    12,
        "icon":     "📈",
        "color":    "#cccccc",
    },
    {
        "title":    "Drift Analysis — Q2 2026",
        "date":     "Apr 2026",
        "model":    "All Models",
        "status":   "Ready",
        "pages":    8,
        "icon":     "📉",
        "color":    "#333333",
    },
    {
        "title":    "SHAP Explainability Audit",
        "date":     "Apr 2026",
        "model":    "churn_predictor_v2",
        "status":   "Ready",
        "pages":    15,
        "icon":     "🔍",
        "color":    "#888888",
    },
    {
        "title":    "Production Reliability Summary",
        "date":     "Mar 2026",
        "model":    "anomaly_detector",
        "status":   "Generating",
        "pages":    0,
        "icon":     "⚙",
        "color":    "#888888",
    },
    {
        "title":    "Model Fairness & Bias Report",
        "date":     "Mar 2026",
        "model":    "credit_score_mlp",
        "status":   "Ready",
        "pages":    20,
        "icon":     "⚖",
        "color":    "#aaaaaa",
    },
    {
        "title":    "Data Quality & Coverage Report",
        "date":     "Feb 2026",
        "model":    "fraud_train_2024",
        "status":   "Ready",
        "pages":    9,
        "icon":     "📋",
        "color":    "#aaaaaa",
    },
]


class ReportsPage(QWidget):
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
        t = QLabel("Reports")
        t.setStyleSheet("font-size: 22px; font-weight: 800; color: #000000; background: transparent;")
        s = QLabel("Generated performance, explainability and audit reports")
        s.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
        col.addWidget(t); col.addWidget(s)
        ph.addLayout(col); ph.addStretch()

        gen_btn = QPushButton("+ Generate Report")
        gen_btn.setObjectName("btn_primary")
        gen_btn.setFixedHeight(36)
        gen_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gen_btn.clicked.connect(lambda: QMessageBox.information(
            self, "Generate Report",
            "Select a model and date range to generate a new report.\n(Report generation coming soon.)"))
        ph.addWidget(gen_btn)
        lay.addLayout(ph)

        # Summary row
        summary = QHBoxLayout()
        summary.setSpacing(14)
        for title, val, color in [
            ("Total Reports", str(len(REPORTS)), "#cccccc"),
            ("Ready",         "5",              "#aaaaaa"),
            ("Generating",    "1",              "#888888"),
            ("Scheduled",     "3",              "#333333"),
        ]:
            card = Card()
            card.setMinimumHeight(80)
            add_shadow(card)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.setSpacing(3)
            vl = QLabel(val)
            vl.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {color}; background: transparent;")
            nl = QLabel(title)
            nl.setStyleSheet("font-size: 10px; color: #888888; background: transparent;")
            cl.addWidget(vl); cl.addWidget(nl)
            summary.addWidget(card)
        lay.addLayout(summary)

        # Report cards
        self._reports_lay = lay
        for report in REPORTS:
            card = Card()
            add_shadow(card)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(18, 16, 18, 16)
            cl.setSpacing(16)

            # Icon box
            icon_box = QWidget()
            icon_box.setFixedSize(50, 50)
            color = report["color"]
            icon_box.setStyleSheet(
                f"background: {color}22; border: 1px solid {color}44; border-radius: 12px;"
            )
            ib_lay = QVBoxLayout(icon_box)
            ib_lay.setContentsMargins(0, 0, 0, 0)
            ic = QLabel(report["icon"])
            ic.setStyleSheet("font-size: 22px; background: transparent;")
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ib_lay.addWidget(ic)
            cl.addWidget(icon_box)

            # Info
            info = QVBoxLayout(); info.setSpacing(4)
            nm = QLabel(report["title"])
            nm.setStyleSheet("font-size: 13px; font-weight: 700; color: #000000; background: transparent;")
            meta_text = f"{report['model']}  ·  {report['date']}"
            if report["pages"]:
                meta_text += f"  ·  {report['pages']} pages"
            meta = QLabel(meta_text)
            meta.setStyleSheet("font-size: 10px; color: #888888; background: transparent;")
            info.addWidget(nm); info.addWidget(meta)
            cl.addLayout(info)
            cl.addStretch()

            # Status badge
            st_color = "#aaaaaa" if report["status"] == "Ready" else "#888888"
            st_badge = QLabel(report["status"])
            st_badge.setStyleSheet(
                f"background: {st_color}22; border: 1px solid {st_color}44; border-radius: 8px; "
                f"color: {st_color}; font-size: 10px; font-weight: 700; padding: 2px 10px;"
            )
            cl.addWidget(st_badge)

            # Action buttons
            btn_style = (
                "QPushButton { background: #f5f5f5; border: 1px solid #d8d8d8; "
                "border-radius: 8px; font-size: 15px; }"
                "QPushButton:hover { background: #e8e8e8; border: 1px solid #cccccc; }"
                "QPushButton:disabled { opacity: 0.3; }"
            )
            for icon, tip in [("⬇", "Download"), ("👁", "Preview"), ("🗑", "Delete")]:
                b = QPushButton(icon)
                b.setFixedSize(32, 32)
                b.setToolTip(tip)
                b.setCursor(Qt.CursorShape.PointingHandCursor)
                b.setEnabled(report["status"] == "Ready")
                b.setStyleSheet(btn_style)
                if tip == "Download":
                    b.clicked.connect(lambda _, r=report: self._download_report(r))
                elif tip == "Preview":
                    b.clicked.connect(lambda _, r=report: QMessageBox.information(
                        self, r["title"],
                        f"Model: {r['model']}\nDate: {r['date']}\nPages: {r['pages']}\nStatus: {r['status']}"))
                elif tip == "Delete":
                    b.clicked.connect(lambda _, c=card: self._delete_report(c))
                cl.addWidget(b)

            lay.addWidget(card)

        lay.addSpacing(10)

    def _download_report(self, report):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", f"{report['title'].replace(' ', '_')}.pdf", "PDF Files (*.pdf)")
        if path:
            QMessageBox.information(self, "Download", f"Report saved to:\n{path}\n(Export not yet connected.)")

    def _delete_report(self, card):
        reply = QMessageBox.question(self, "Delete Report",
            "Delete this report permanently?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            card.setParent(None)
            card.deleteLater()
