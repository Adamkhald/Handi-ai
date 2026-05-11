"""
HandiAI — Model Metrics Page
Shows static fallback data on load; updates with real values when
engine.metrics_computed fires (after Upload & Analyze).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QComboBox
)
from PySide6.QtCore import Qt

import data
from widgets.components import Card, add_shadow
from charts.matplotlib_charts import ConfusionMatrixChart, ROCCurveChart, PRCurveChart


def _make_metric_card(name, value_str, color, icon):
    """Returns (card_widget, value_label) so the label can be updated later."""
    card = Card()
    card.setMinimumHeight(90)
    lay  = QVBoxLayout(card)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(4)

    top = QHBoxLayout()
    icon_lbl = QLabel(icon)
    icon_lbl.setStyleSheet(f"font-size: 18px; color: {color}; background: transparent;")
    top.addWidget(icon_lbl); top.addStretch()
    lay.addLayout(top)

    val_lbl = QLabel(value_str)
    val_lbl.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {color}; background: transparent;")
    lay.addWidget(val_lbl)

    name_lbl = QLabel(name)
    name_lbl.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
    lay.addWidget(name_lbl)

    add_shadow(card)
    return card, val_lbl


class MetricsPage(QWidget):
    def __init__(self, engine=None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setObjectName("page_container")
        self._metric_val_labels = {}   # name → QLabel
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

        # ── Header ────────────────────────────────────────────
        ph = QHBoxLayout()
        col = QVBoxLayout(); col.setSpacing(2)
        t = QLabel("Model Metrics")
        t.setStyleSheet("font-size: 22px; font-weight: 800; color: #000000; background: transparent;")
        self._sub_lbl = QLabel("Evaluation results  ·  Upload a model to see real metrics")
        self._sub_lbl.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
        col.addWidget(t); col.addWidget(self._sub_lbl)
        ph.addLayout(col); ph.addStretch()

        combo = QComboBox()
        for m in data.MODELS[:6]:
            combo.addItem(m["name"])
        combo.setFixedWidth(200); combo.setFixedHeight(36)
        ph.addWidget(combo)

        btn = QPushButton("↺  Re-evaluate")
        btn.setObjectName("btn_primary")
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ph.addWidget(btn)
        lay.addLayout(ph)

        # ── Row 1: 5 metric pills ─────────────────────────────
        metrics_row = QHBoxLayout(); metrics_row.setSpacing(14)
        pill_configs = [
            ("Accuracy",  "#cccccc", "◎"),
            ("Precision", "#333333", "▣"),
            ("Recall",    "#888888", "◈"),
            ("F1-Score",  "#aaaaaa", "⬡"),
            ("ROC-AUC",   "#aaaaaa", "◉"),
        ]
        for name, color, icon in pill_configs:
            card, lbl = _make_metric_card(name, "—", color, icon)
            self._metric_val_labels[name] = lbl
            metrics_row.addWidget(card)
        lay.addLayout(metrics_row)

        # ── Row 2: Confusion Matrix + ROC + PR ────────────────
        row2 = QHBoxLayout(); row2.setSpacing(16)

        cm_card = Card(); add_shadow(cm_card)
        cm_lay  = QVBoxLayout(cm_card)
        cm_lay.setContentsMargins(16, 14, 16, 14); cm_lay.setSpacing(8)
        cm_t = QLabel("Confusion Matrix")
        cm_t.setStyleSheet("font-size: 13px; font-weight: 700; color: #000000; background: transparent;")
        self._cm_sub = QLabel(f"Test Set · {len(data.CONFUSION_LABELS)} Classes")
        self._cm_sub.setStyleSheet("font-size: 10px; color: #888888; background: transparent;")
        cm_lay.addWidget(cm_t); cm_lay.addWidget(self._cm_sub)
        self._cm_chart = ConfusionMatrixChart()
        cm_lay.addWidget(self._cm_chart)
        row2.addWidget(cm_card, 1)

        roc_card = Card(); add_shadow(roc_card)
        roc_lay  = QVBoxLayout(roc_card)
        roc_lay.setContentsMargins(16, 14, 16, 14); roc_lay.setSpacing(8)
        roc_t = QLabel("ROC Curve")
        roc_t.setStyleSheet("font-size: 13px; font-weight: 700; color: #000000; background: transparent;")
        self._roc_sub = QLabel("AUC = —")
        self._roc_sub.setStyleSheet("font-size: 10px; color: #222222; font-weight: 700; background: transparent;")
        roc_lay.addWidget(roc_t); roc_lay.addWidget(self._roc_sub)
        self._roc_chart = ROCCurveChart()
        roc_lay.addWidget(self._roc_chart)
        row2.addWidget(roc_card, 1)

        pr_card = Card(); add_shadow(pr_card)
        pr_lay  = QVBoxLayout(pr_card)
        pr_lay.setContentsMargins(16, 14, 16, 14); pr_lay.setSpacing(8)
        pr_t = QLabel("Precision–Recall Curve")
        pr_t.setStyleSheet("font-size: 13px; font-weight: 700; color: #000000; background: transparent;")
        self._pr_sub = QLabel("Average Precision = —")
        self._pr_sub.setStyleSheet("font-size: 10px; color: #000000; font-weight: 700; background: transparent;")
        pr_lay.addWidget(pr_t); pr_lay.addWidget(self._pr_sub)
        self._pr_chart = PRCurveChart()
        pr_lay.addWidget(self._pr_chart)
        row2.addWidget(pr_card, 1)

        lay.addLayout(row2)

        # ── Row 3: Per-class breakdown ────────────────────────
        self._breakdown_card = Card(); add_shadow(self._breakdown_card)
        bl = QVBoxLayout(self._breakdown_card)
        bl.setContentsMargins(20, 16, 20, 16); bl.setSpacing(12)

        bt = QLabel("Per-Class Performance Breakdown")
        bt.setStyleSheet("font-size: 13px; font-weight: 700; color: #000000; background: transparent;")
        bl.addWidget(bt)

        # Fixed header
        hdr = QHBoxLayout()
        for col_name in ["Class", "Precision", "Recall", "F1", "Support"]:
            lbl = QLabel(col_name.upper())
            lbl.setStyleSheet(
                "font-size: 10px; font-weight: 700; color: #444444; "
                "letter-spacing: 0.8px; background: transparent;"
            )
            hdr.addWidget(lbl, 1)
        bl.addLayout(hdr)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #e0e0e0; max-height: 1px;")
        bl.addWidget(sep)

        # Dynamic rows container
        self._per_class_container = QWidget()
        self._per_class_container.setStyleSheet("background: transparent;")
        self._per_class_lay = QVBoxLayout(self._per_class_container)
        self._per_class_lay.setContentsMargins(0, 0, 0, 0)
        self._per_class_lay.setSpacing(0)
        bl.addWidget(self._per_class_container)

        self._rebuild_per_class(self._default_per_class())
        lay.addWidget(self._breakdown_card)
        lay.addSpacing(10)

    def _connect_engine(self):
        self.engine.metrics_computed.connect(self._on_metrics_computed)

    def _on_metrics_computed(self, results):
        m   = results["metrics"]
        mdl = results.get("model_name", "uploaded_model")
        n   = results["n_samples"]

        self._sub_lbl.setText(
            f"{results['model_type']}  ·  {n:,} samples  ·  "
            f"{len(results['class_labels'])} classes"
        )

        for name, key in [
            ("Accuracy",  "accuracy"),
            ("Precision", "precision"),
            ("Recall",    "recall"),
            ("F1-Score",  "f1_score"),
            ("ROC-AUC",   "roc_auc"),
        ]:
            if name in self._metric_val_labels:
                self._metric_val_labels[name].setText(f"{m[key]:.1f}%")

        roc = results.get("roc_curve", {})
        self._cm_chart.update_data(results["confusion_matrix"], results["class_labels"])
        self._cm_sub.setText(f"Test Set · {len(results['class_labels'])} Classes")

        self._roc_chart.update_data(
            roc.get("fpr", [0, 1]), roc.get("tpr", [0, 1]), roc.get("auc", 0.0)
        )
        self._roc_sub.setText(f"AUC = {roc.get('auc', 0.0):.1f}%")

        pr = results.get("pr_curve", {})
        self._pr_chart.update_data(
            pr.get("recall", [0, 1]), pr.get("precision", [1, 0]), pr.get("ap", 0.0)
        )
        self._pr_sub.setText(f"Average Precision = {pr.get('ap', 0.0):.3f}")

        self._rebuild_per_class(results.get("per_class", []))

    def _rebuild_per_class(self, per_class_data):
        CLASS_COLORS = ["#555555", "#333333", "#888888", "#444444",
                        "#666666", "#777777", "#888888", "#999999"]

        while self._per_class_lay.count():
            item = self._per_class_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not per_class_data:
            empty = QLabel("No data yet — upload a model and dataset to see per-class metrics.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(
                "font-size: 12px; color: #444444; padding: 16px 0; background: transparent;"
            )
            self._per_class_lay.addWidget(empty)
            return

        for i, row_data in enumerate(per_class_data):
            color = CLASS_COLORS[i % len(CLASS_COLORS)]
            row   = QHBoxLayout()

            cls_lbl = QLabel(str(row_data["class"]))
            cls_lbl.setStyleSheet(
                f"font-size: 12px; font-weight: 600; color: {color}; background: transparent;"
            )
            row.addWidget(cls_lbl, 1)

            for val in [
                f"{row_data['precision']:.1f}%",
                f"{row_data['recall']:.1f}%",
                f"{row_data['f1']:.1f}%",
                str(row_data["support"]),
            ]:
                lbl = QLabel(val)
                lbl.setStyleSheet("font-size: 11px; color: #222222; background: transparent;")
                row.addWidget(lbl, 1)

            self._per_class_lay.addLayout(row)

            if i < len(per_class_data) - 1:
                sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
                sep.setStyleSheet("background: #e0e0e0; max-height: 1px;")
                self._per_class_lay.addWidget(sep)

    @staticmethod
    def _default_per_class():
        return []
