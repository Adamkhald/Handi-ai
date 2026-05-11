"""
HandiAI — Production Logs Page
"""

import csv
import random
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QTextEdit, QComboBox, QLineEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QTimer

import data
from widgets.components import Card, add_shadow


class ProductionLogsPage(QWidget):
    def __init__(self, engine=None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setObjectName("page_container")
        self._setup_ui()
        if self.engine:
            self._connect_engine()

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
        t = QLabel("Production Logs")
        t.setStyleSheet("font-size: 22px; font-weight: 800; color: #000000; background: transparent;")
        s = QLabel("Real-time prediction logs, audit trail and SHAP explanations")
        s.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
        col.addWidget(t); col.addWidget(s)
        ph.addLayout(col); ph.addStretch()
        export_btn = QPushButton("⬇  Export CSV")
        export_btn.setObjectName("btn_secondary")
        export_btn.setFixedHeight(36)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self._export_csv)
        ph.addWidget(export_btn)
        lay.addLayout(ph)

        # Filters row
        filter_card = Card()
        add_shadow(filter_card)
        fl = QHBoxLayout(filter_card)
        fl.setContentsMargins(16, 10, 16, 10)
        fl.setSpacing(12)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter logs…")
        self._search.setFixedHeight(34)
        self._search.setStyleSheet(
            "QLineEdit { background: #f2f2f2; border: 1px solid #d8d8d8; border-radius: 8px; "
            "padding: 0 12px; color: #222222; font-size: 12px; }"
            "QLineEdit:focus { border: 1px solid #888888; }"
        )
        fl.addWidget(self._search, 2)

        self._filter_combos = []
        for label, items in [
            ("Model", ["All Models"] + [m["name"] for m in data.MODELS[:5]]),
            ("Prediction", ["All", "Fraud", "Normal", "Anomaly", "High-Risk"]),
            ("Status", ["All", "OK", "Drift Flagged", "High Latency"]),
        ]:
            combo = QComboBox()
            for item in items:
                combo.addItem(item)
            combo.setFixedHeight(34)
            fl.addWidget(combo, 1)
            self._filter_combos.append(combo)

        clr_btn = QPushButton("Clear Filters")
        clr_btn.setObjectName("btn_secondary")
        clr_btn.setFixedHeight(34)
        clr_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clr_btn.clicked.connect(self._clear_filters)
        fl.addWidget(clr_btn)
        lay.addWidget(filter_card)

        # Log viewer
        log_card = Card()
        add_shadow(log_card)
        ll = QVBoxLayout(log_card)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)

        # Log header bar
        log_hdr = QWidget()
        log_hdr.setStyleSheet("background: #f0f0f0; border-radius: 16px 16px 0 0;")
        lh_lay = QHBoxLayout(log_hdr)
        lh_lay.setContentsMargins(18, 10, 18, 10)
        lh_lay.setSpacing(16)
        for col_name, w in [("TIMESTAMP", 80), ("MODEL", 160), ("PREDICTED", 90),
                             ("CONFIDENCE", 90), ("LATENCY", 80), ("DRIFT", 60), ("FEATURES", 200)]:
            lbl = QLabel(col_name)
            lbl.setFixedWidth(w)
            lbl.setStyleSheet(
                "font-size: 9px; font-weight: 700; color: #444444; "
                "letter-spacing: 1px; background: transparent;"
            )
            lh_lay.addWidget(lbl)
        lh_lay.addStretch()
        ll.addWidget(log_hdr)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #e0e0e0; max-height: 1px;")
        ll.addWidget(sep)

        # Scrollable rows area
        rows_scroll = QScrollArea()
        rows_scroll.setWidgetResizable(True)
        rows_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        rows_scroll.setMinimumHeight(380)

        rows_widget = QWidget()
        rows_widget.setStyleSheet("background: transparent;")
        self._rows_lay = QVBoxLayout(rows_widget)
        self._rows_lay.setContentsMargins(0, 4, 0, 4)
        self._rows_lay.setSpacing(0)
        rows_scroll.setWidget(rows_widget)
        ll.addWidget(rows_scroll)

        # Placeholder shown until real data arrives
        self._empty_lbl = QLabel("No predictions yet — upload a model and dataset to see real logs here.")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.setStyleSheet(
            "font-size: 12px; color: #444444; padding: 32px 0; background: transparent;"
        )
        self._rows_lay.addWidget(self._empty_lbl)
        self._rows_lay.addStretch()
        lay.addWidget(log_card)
        lay.addSpacing(10)

    def _connect_engine(self):
        self.engine.log_entry_added.connect(self._on_log)


    def _add_log_row(self, entry, insert_at_top=False):
        PRED_COLORS = {
            "Fraud":     "#111111",
            "Normal":    "#aaaaaa",
            "Anomaly":   "#888888",
            "High-Risk": "#888888",
        }
        pred = entry["predicted"]
        pc   = PRED_COLORS.get(pred, "#888888")

        row_widget = QWidget()
        row_widget.setStyleSheet(
            "QWidget { background: transparent; }"
            "QWidget:hover { background: rgba(0,0,0,0.04); }"
        )
        row_lay = QHBoxLayout(row_widget)
        row_lay.setContentsMargins(18, 8, 18, 8)
        row_lay.setSpacing(16)

        def cell(text, width, color="#888888", bold=False):
            lbl = QLabel(text)
            lbl.setFixedWidth(width)
            weight = "font-weight: 600;" if bold else ""
            lbl.setStyleSheet(
                f"font-size: 11px; color: {color}; font-family: 'Consolas'; {weight} background: transparent;"
            )
            return lbl

        row_lay.addWidget(cell(entry["timestamp"], 80))
        row_lay.addWidget(cell(entry["model"][:22], 160))
        pred_lbl = cell(pred, 90, pc, True)
        row_lay.addWidget(pred_lbl)
        row_lay.addWidget(cell(f"{entry['confidence']:.1f}%", 90, "#cccccc", True))
        lat_color = "#888888" if entry["latency_ms"] < 50 else ("#555555" if entry["latency_ms"] < 100 else "#111111")
        row_lay.addWidget(cell(f"{entry['latency_ms']:.0f} ms", 80, lat_color))

        drift_lbl = QLabel("⚑ Yes" if entry.get("drift_flag") else "—")
        drift_lbl.setFixedWidth(60)
        drift_lbl.setStyleSheet(
            f"font-size: 11px; color: {'#888888' if entry.get('drift_flag') else '#2a2a2a'}; background: transparent;"
        )
        row_lay.addWidget(drift_lbl)

        feats = ", ".join(entry.get("top_features", [])[:2])
        row_lay.addWidget(cell(feats, 200, "#444444"))
        row_lay.addStretch()

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #f0f0f0; max-height: 1px;")

        if insert_at_top:
            self._rows_lay.insertWidget(0, sep)
            self._rows_lay.insertWidget(0, row_widget)
        else:
            self._rows_lay.addWidget(row_widget)
            self._rows_lay.addWidget(sep)
            
    def _on_log(self, entry):
        if not hasattr(self, "_log_entries"):
            self._log_entries = []
        self._log_entries.insert(0, entry)
        if len(self._log_entries) > 500:
            self._log_entries = self._log_entries[:500]
        if hasattr(self, "_empty_lbl") and self._empty_lbl.isVisible():
            self._empty_lbl.hide()
        self._add_log_row(entry, insert_at_top=True)
        if self._rows_lay.count() > 100:
            w1 = self._rows_lay.takeAt(self._rows_lay.count() - 2)
            w2 = self._rows_lay.takeAt(self._rows_lay.count() - 2)
            if w1 and w1.widget(): w1.widget().deleteLater()
            if w2 and w2.widget(): w2.widget().deleteLater()

    def _clear_filters(self):
        self._search.clear()
        for combo in self._filter_combos:
            combo.setCurrentIndex(0)

    def _export_csv(self):
        entries = getattr(self, "_log_entries", [])
        if not entries:
            QMessageBox.information(self, "Export CSV", "No log entries to export yet.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", "production_logs.csv", "CSV Files (*.csv)")
        if not path:
            return
        fields = ["timestamp", "model", "predicted", "confidence", "latency_ms", "drift_flag"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(entries)
        QMessageBox.information(self, "Export CSV", f"Saved {len(entries)} rows to:\n{path}")

