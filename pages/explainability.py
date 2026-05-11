"""
HandiAI — Explainability Page
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt

import data
from widgets.components import Card, SHAPBarChart, make_label, add_shadow
from charts.matplotlib_charts import SHAPWaterfallChart, FeatureImportanceChart


class ExplainabilityPage(QWidget):
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
        pg_title = QLabel("Explainability")
        pg_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; background: transparent;")
        pg_sub = QLabel("SHAP-based model interpretability for fraud_detector_v3")
        pg_sub.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        ph_col = QVBoxLayout(); ph_col.setSpacing(2)
        ph_col.addWidget(pg_title); ph_col.addWidget(pg_sub)
        ph.addLayout(ph_col); ph.addStretch()
        btn = QPushButton("⟳  Re-Explain")
        btn.setObjectName("btn_primary")
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ph.addWidget(btn)
        lay.addLayout(ph)

        # ── Row 1: Why Did Model Predict + Waterfall ──────────
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        # WHY panel
        why_card = Card()
        add_shadow(why_card)
        why_lay = QVBoxLayout(why_card)
        why_lay.setContentsMargins(18, 16, 18, 16)
        why_lay.setSpacing(10)

        why_title = QLabel("WHY DID THE MODEL PREDICT THIS?")
        why_title.setStyleSheet(
            "font-size: 11px; font-weight: 800; color: #b46cff; "
            "letter-spacing: 1.5px; background: transparent;"
        )
        why_lay.addWidget(why_title)

        # Placeholder — replaced with real data after upload
        placeholder = QLabel(
            "Upload a model and dataset to see a real prediction explanation here.\n\n"
            "SHAP charts on the right will update automatically."
        )
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setWordWrap(True)
        placeholder.setStyleSheet(
            "font-size: 12px; color: #5a5888; padding: 20px 8px; background: transparent;"
        )
        why_lay.addWidget(placeholder)

        why_lay.addStretch()
        row1.addWidget(why_card, 1)

        # Waterfall chart
        waterfall_card = Card()
        add_shadow(waterfall_card)
        wf_lay = QVBoxLayout(waterfall_card)
        wf_lay.setContentsMargins(16, 14, 16, 14)
        wf_lay.setSpacing(8)
        wf_title = QLabel("SHAP Waterfall Plot")
        wf_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        wf_lay.addWidget(wf_title)
        self._wf_chart = SHAPWaterfallChart()
        wf_lay.addWidget(self._wf_chart)
        row1.addWidget(waterfall_card, 2)

        lay.addLayout(row1)

        # ── Row 2: Feature Importance + SHAP bar ─────────────
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        feat_card = Card()
        add_shadow(feat_card)
        fl = QVBoxLayout(feat_card)
        fl.setContentsMargins(16, 14, 16, 14)
        fl.setSpacing(8)
        ft = QLabel("Feature Importance (Global)")
        ft.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        fl.addWidget(ft)
        self._fi_chart = FeatureImportanceChart()
        fl.addWidget(self._fi_chart)
        row2.addWidget(feat_card, 1)

        # Local SHAP bars
        local_card = Card()
        add_shadow(local_card)
        ll = QVBoxLayout(local_card)
        ll.setContentsMargins(16, 14, 16, 14)
        ll.setSpacing(8)
        lt = QLabel("Local SHAP Values — This Prediction")
        lt.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        ll.addWidget(lt)
        self._shap_bars = SHAPBarChart(data.SHAP_FEATURES)
        ll.addWidget(self._shap_bars)
        row2.addWidget(local_card, 1)

        lay.addLayout(row2)

        lay.addSpacing(10)

    def _connect_engine(self):
        self.engine.shap_updated.connect(self._on_shap)
        self._on_shap(self.engine.snapshot_shap())

    def _on_shap(self, features):
        self._wf_chart.update_features(features)
        self._fi_chart.update_features(features)
        self._shap_bars.set_features(features)
