"""
HandiAI — Models Page
Shows loaded model info synced from the engine after upload.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt

import data
from widgets.components import Card, add_shadow


class ModelsPage(QWidget):
    def __init__(self, engine=None, navigate_fn=None, parent=None):
        super().__init__(parent)
        self.engine      = engine
        self._navigate   = navigate_fn
        self._model_info = None          # populated by engine signal
        self.setObjectName("page_container")
        self._setup_ui()
        if self.engine:
            self._connect_engine()

    # ── Engine wiring ──────────────────────────────────────────
    def _connect_engine(self):
        self.engine.metrics_computed.connect(self._on_results)

    def _on_results(self, results: dict):
        self._model_info = results
        self._refresh_table()

    # ── UI ─────────────────────────────────────────────────────
    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._content = QWidget()
        self._content.setObjectName("page_container")
        scroll.setWidget(self._content)
        outer.addWidget(scroll)

        self._lay = QVBoxLayout(self._content)
        self._lay.setContentsMargins(24, 24, 24, 24)
        self._lay.setSpacing(20)

        # Header
        ph = QHBoxLayout()
        col = QVBoxLayout(); col.setSpacing(2)
        t = QLabel("Models")
        t.setStyleSheet("font-size: 22px; font-weight: 800; color: #000000; background: transparent;")
        s = QLabel("Loaded model registry — updated automatically after upload & analysis")
        s.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
        col.addWidget(t); col.addWidget(s)
        ph.addLayout(col); ph.addStretch()

        self._upload_btn = QPushButton("↑  Upload & Analyze")
        self._upload_btn.setObjectName("btn_primary")
        self._upload_btn.setFixedHeight(36)
        self._upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._upload_btn.clicked.connect(lambda: self._navigate and self._navigate(1))
        ph.addWidget(self._upload_btn)
        self._lay.addLayout(ph)

        # Model table card (holds placeholder or real rows)
        self._table_card = Card()
        add_shadow(self._table_card)
        self._table_lay = QVBoxLayout(self._table_card)
        self._table_lay.setContentsMargins(20, 18, 20, 18)
        self._table_lay.setSpacing(12)

        # Table header
        hdr = QHBoxLayout()
        for col_name, stretch in [
            ("Model Name", 3), ("Type", 2), ("Task", 1),
            ("Accuracy / R²", 1), ("Samples", 1), ("Features", 1), ("Status", 1),
        ]:
            lbl = QLabel(col_name.upper())
            lbl.setStyleSheet(
                "font-size: 9px; font-weight: 700; color: #444444; "
                "letter-spacing: 0.8px; background: transparent;"
            )
            hdr.addWidget(lbl, stretch)
        self._table_lay.addLayout(hdr)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #e0e0e0; max-height: 1px;")
        self._table_lay.addWidget(sep)

        # Placeholder
        self._placeholder = QLabel(
            "No model loaded yet.\n\nUse  ↑ Upload & Analyze  to import your first model."
        )
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setWordWrap(True)
        self._placeholder.setStyleSheet(
            "font-size: 12px; color: #444444; padding: 32px 0; background: transparent;"
        )
        self._table_lay.addWidget(self._placeholder)

        self._lay.addWidget(self._table_card)
        self._lay.addStretch()

    def _refresh_table(self):
        r = self._model_info
        if not r:
            return

        # Remove old pills card from outer layout if it exists
        if hasattr(self, "_pills_card") and self._pills_card is not None:
            self._lay.removeWidget(self._pills_card)
            self._pills_card.deleteLater()
            self._pills_card = None

        # Hide placeholder, clear all rows from table (keep: header row, sep = first 2 items)
        self._placeholder.hide()
        while self._table_lay.count() > 3:
            item = self._table_lay.takeAt(3)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        m        = r["metrics"]
        task     = r.get("task_type", "classification")
        acc_val  = f"{m['accuracy']:.1f}%" if task == "classification" else f"{m.get('r2', 0):.4f}"
        acc_lbl  = "Accuracy" if task == "classification" else "R²"

        # ── Model row ──────────────────────────────────────────
        row = QHBoxLayout(); row.setSpacing(0)

        def cell(text, stretch, bold=False, color="#333333"):
            lbl = QLabel(text)
            lbl.setStyleSheet(
                f"font-size: 11px; color: {color}; "
                f"{'font-weight: 700;' if bold else ''} background: transparent;"
            )
            lbl.setWordWrap(True)
            row.addWidget(lbl, stretch)

        cell(r.get("model_name", "—"),      3, bold=True, color="#000000")
        cell(r.get("model_type", "—"),      2)
        cell(task.capitalize(),             1)
        cell(acc_val,                       1, bold=True)
        cell(f"{r['n_samples']:,}",         1)
        cell(str(r["n_features"]),          1)

        badge = QLabel("● Active")
        badge.setStyleSheet(
            "background: #e8f5e9; border: 1px solid #a5d6a7; border-radius: 8px; "
            "color: #2e7d32; font-size: 10px; font-weight: 700; padding: 2px 10px;"
        )
        row.addWidget(badge, 1)

        self._table_lay.addLayout(row)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background: #f0f0f0; max-height: 1px;")
        self._table_lay.addWidget(sep2)

        # ── Metric pills row ───────────────────────────────────
        pills_card = Card()
        add_shadow(pills_card)
        pills_lay = QVBoxLayout(pills_card)
        pills_lay.setContentsMargins(18, 14, 18, 14)
        pills_lay.setSpacing(10)

        ph_t = QLabel("Performance Summary")
        ph_t.setStyleSheet("font-size: 13px; font-weight: 700; color: #000000; background: transparent;")
        pills_lay.addWidget(ph_t)

        pills_row = QHBoxLayout(); pills_row.setSpacing(12)

        if task == "classification":
            metrics = [
                ("Accuracy",  f"{m['accuracy']:.1f}%"),
                ("Precision", f"{m['precision']:.1f}%"),
                ("Recall",    f"{m['recall']:.1f}%"),
                ("F1 Score",  f"{m['f1_score']:.1f}%"),
                ("ROC AUC",   f"{m['roc_auc']:.1f}%"),
            ]
        else:
            metrics = [
                ("R²",   f"{m.get('r2', 0):.4f}"),
                ("MAE",  f"{m.get('mae', 0):.4f}"),
                ("RMSE", f"{m.get('rmse', 0):.4f}"),
                ("MSE",  f"{m.get('mse', 0):.4f}"),
            ]

        for name, val in metrics:
            pill = QWidget()
            pill.setStyleSheet(
                "background: #f5f5f5; border: 1px solid #e0e0e0; border-radius: 10px;"
            )
            pl = QVBoxLayout(pill)
            pl.setContentsMargins(16, 10, 16, 10)
            pl.setSpacing(2)
            vl = QLabel(val)
            vl.setStyleSheet("font-size: 18px; font-weight: 800; color: #000000; background: transparent;")
            nl = QLabel(name)
            nl.setStyleSheet("font-size: 10px; color: #888888; background: transparent;")
            pl.addWidget(vl); pl.addWidget(nl)
            pills_row.addWidget(pill, 1)

        pills_lay.addLayout(pills_row)

        # Feature list
        feats = r.get("feature_names", [])
        if feats:
            feat_lbl = QLabel("Features:  " + "  ·  ".join(feats[:10]))
            feat_lbl.setWordWrap(True)
            feat_lbl.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
            pills_lay.addWidget(feat_lbl)

        self._pills_card = pills_card
        self._lay.insertWidget(self._lay.count() - 1, pills_card)
