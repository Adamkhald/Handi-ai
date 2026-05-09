"""
HandiAI — Model Metrics Page
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import data
from widgets.components import Card, add_shadow
from charts.matplotlib_charts import ConfusionMatrixChart, ROCCurveChart, PRCurveChart


def _metric_mini_card(name, value, color, icon):
    """Small metric pill card."""
    card = Card()
    card.setMinimumHeight(90)
    lay = QVBoxLayout(card)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(4)

    top = QHBoxLayout()
    icon_lbl = QLabel(icon)
    icon_lbl.setStyleSheet(f"font-size: 18px; color: {color}; background: transparent;")
    top.addWidget(icon_lbl)
    top.addStretch()
    lay.addLayout(top)

    val_lbl = QLabel(f"{value:.1f}%" if isinstance(value, float) else str(value))
    val_lbl.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {color}; background: transparent;")
    lay.addWidget(val_lbl)

    name_lbl = QLabel(name)
    name_lbl.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
    lay.addWidget(name_lbl)

    add_shadow(card)
    return card


class MetricsPage(QWidget):
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

        # ── Header ────────────────────────────────────────────
        ph = QHBoxLayout()
        col = QVBoxLayout(); col.setSpacing(2)
        t = QLabel("Model Metrics")
        t.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; background: transparent;")
        s = QLabel("Evaluation results for fraud_detector_v3 · XGBoost · Test split: 20%")
        s.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        col.addWidget(t); col.addWidget(s)
        ph.addLayout(col); ph.addStretch()

        # Model selector
        combo = QComboBox()
        for m in data.MODELS[:6]:
            combo.addItem(m["name"])
        combo.setFixedWidth(200)
        combo.setFixedHeight(36)
        ph.addWidget(combo)

        btn = QPushButton("↺  Re-evaluate")
        btn.setObjectName("btn_primary")
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ph.addWidget(btn)
        lay.addLayout(ph)

        # ── Row 1: 5 metric pills ─────────────────────────────
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(14)
        metric_configs = [
            ("Accuracy",  data.MODEL_METRICS["accuracy"],  "#00e0b8", "◎"),
            ("Precision", data.MODEL_METRICS["precision"], "#b46cff", "▣"),
            ("Recall",    data.MODEL_METRICS["recall"],    "#ffd400", "◈"),
            ("F1-Score",  data.MODEL_METRICS["f1_score"],  "#00c97d", "⬡"),
            ("ROC-AUC",   data.MODEL_METRICS["roc_auc"],   "#4d9fff", "◉"),
        ]
        for name, val, color, icon in metric_configs:
            metrics_row.addWidget(_metric_mini_card(name, val, color, icon))
        lay.addLayout(metrics_row)

        # ── Row 2: Confusion Matrix + ROC Curve + PR Curve ───
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        # Confusion Matrix
        cm_card = Card()
        add_shadow(cm_card)
        cm_lay = QVBoxLayout(cm_card)
        cm_lay.setContentsMargins(16, 14, 16, 14)
        cm_lay.setSpacing(8)
        cm_t = QLabel("Confusion Matrix")
        cm_t.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        cm_s = QLabel("Test Set · 4 Classes")
        cm_s.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
        cm_lay.addWidget(cm_t)
        cm_lay.addWidget(cm_s)
        cm_lay.addWidget(ConfusionMatrixChart())
        row2.addWidget(cm_card, 1)

        # ROC Curve
        roc_card = Card()
        add_shadow(roc_card)
        roc_lay = QVBoxLayout(roc_card)
        roc_lay.setContentsMargins(16, 14, 16, 14)
        roc_lay.setSpacing(8)
        roc_t = QLabel("ROC Curve")
        roc_t.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        roc_s = QLabel(f"AUC = {data.MODEL_METRICS['roc_auc']:.1f}%")
        roc_s.setStyleSheet("font-size: 10px; color: #00e0b8; font-weight: 700; background: transparent;")
        roc_lay.addWidget(roc_t)
        roc_lay.addWidget(roc_s)
        roc_lay.addWidget(ROCCurveChart())
        row2.addWidget(roc_card, 1)

        # PR Curve
        pr_card = Card()
        add_shadow(pr_card)
        pr_lay = QVBoxLayout(pr_card)
        pr_lay.setContentsMargins(16, 14, 16, 14)
        pr_lay.setSpacing(8)
        pr_t = QLabel("Precision–Recall Curve")
        pr_t.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        pr_s = QLabel("Average Precision = 0.962")
        pr_s.setStyleSheet("font-size: 10px; color: #b46cff; font-weight: 700; background: transparent;")
        pr_lay.addWidget(pr_t)
        pr_lay.addWidget(pr_s)
        pr_lay.addWidget(PRCurveChart())
        row2.addWidget(pr_card, 1)

        lay.addLayout(row2)

        # ── Row 3: Per-class breakdown table ─────────────────
        breakdown_card = Card()
        add_shadow(breakdown_card)
        bl = QVBoxLayout(breakdown_card)
        bl.setContentsMargins(20, 16, 20, 16)
        bl.setSpacing(12)

        bt = QLabel("Per-Class Performance Breakdown")
        bt.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        bl.addWidget(bt)

        # Header row
        hdr = QHBoxLayout()
        for col_name in ["Class", "Precision", "Recall", "F1", "Support", "AUC"]:
            lbl = QLabel(col_name.upper())
            lbl.setStyleSheet(
                "font-size: 10px; font-weight: 700; color: #5a5888; "
                "letter-spacing: 0.8px; background: transparent;"
            )
            hdr.addWidget(lbl, 1)
        bl.addLayout(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #2e2b5f; max-height: 1px;")
        bl.addWidget(sep)

        import random
        class_colors = ["#00e0b8", "#b46cff", "#ffd400", "#ff5577"]
        for i, cls in enumerate(data.CONFUSION_LABELS):
            row = QHBoxLayout()
            prec = round(random.uniform(0.88, 0.98), 3)
            rec  = round(random.uniform(0.85, 0.97), 3)
            f1   = round(2 * prec * rec / (prec + rec), 3)
            supp = data.CONFUSION_MATRIX[i][i] + sum(
                data.CONFUSION_MATRIX[j][i] for j in range(len(data.CONFUSION_LABELS)) if j != i
            )
            auc  = round(random.uniform(0.94, 0.995), 3)

            color = class_colors[i]

            cls_lbl = QLabel(cls)
            cls_lbl.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {color}; background: transparent;")
            row.addWidget(cls_lbl, 1)

            for val in [f"{prec:.3f}", f"{rec:.3f}", f"{f1:.3f}", str(supp), f"{auc:.3f}"]:
                lbl = QLabel(val)
                lbl.setStyleSheet("font-size: 11px; color: #e0dff5; background: transparent;")
                row.addWidget(lbl, 1)

            bl.addLayout(row)

            if cls != data.CONFUSION_LABELS[-1]:
                sep2 = QFrame()
                sep2.setFrameShape(QFrame.Shape.HLine)
                sep2.setStyleSheet("background: #2a2855; max-height: 1px;")
                bl.addWidget(sep2)

        lay.addWidget(breakdown_card)
        lay.addSpacing(10)
