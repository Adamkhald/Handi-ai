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

        # Prediction result
        pred_card = QWidget()
        pred_card.setStyleSheet(
            "background: rgba(255,85,119,0.12); border: 1px solid #ff557744; border-radius: 10px;"
        )
        pc_lay = QHBoxLayout(pred_card)
        pc_lay.setContentsMargins(12, 10, 12, 10)

        pred_icon = QLabel("⚠")
        pred_icon.setStyleSheet("font-size: 22px; color: #ff5577; background: transparent;")
        pc_lay.addWidget(pred_icon)

        pred_text = QVBoxLayout(); pred_text.setSpacing(2)
        pred_label = QLabel("FRAUD DETECTED")
        pred_label.setStyleSheet(
            "font-size: 14px; font-weight: 800; color: #ff5577; background: transparent;"
        )
        conf_label = QLabel("Confidence: 94.7%  ·  Threshold: 80%")
        conf_label.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        pred_text.addWidget(pred_label); pred_text.addWidget(conf_label)
        pc_lay.addLayout(pred_text)
        pc_lay.addStretch()
        why_lay.addWidget(pred_card)

        # Input values
        inputs_title = QLabel("Input Values")
        inputs_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #ffffff; background: transparent;")
        why_lay.addWidget(inputs_title)

        input_data = [
            ("transaction_amount", "$2,450.00"),
            ("merchant_category",  "Electronics"),
            ("time_of_day",        "02:34 AM"),
            ("location_mismatch",  "True ⚠"),
            ("user_history_score", "0.23 (low)"),
        ]
        for key, val in input_data:
            row = QHBoxLayout()
            k = QLabel(key)
            k.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
            v = QLabel(val)
            v.setStyleSheet("font-size: 11px; font-weight: 600; color: #ffffff; background: transparent;")
            row.addWidget(k)
            row.addStretch()
            row.addWidget(v)
            why_lay.addLayout(row)

        # Timeline
        timeline_title = QLabel("Reasoning Timeline")
        timeline_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #ffffff; background: transparent;")
        why_lay.addWidget(timeline_title)
        timeline_items = [
            ("Baseline prediction",      "50.0%",  "#9896c8"),
            ("+ transaction_amount",     "+15.2%", "#00c97d"),
            ("+ location_mismatch",      "+12.8%", "#00c97d"),
            ("− user_history_score",     "−8.1%",  "#ff5577"),
            ("+ time_of_day (2AM)",      "+11.3%", "#00c97d"),
            ("+ merchant_category",      "+13.5%", "#00c97d"),
            ("= Final: FRAUD",           "94.7%",  "#ff5577"),
        ]
        for step, val, color in timeline_items:
            row = QHBoxLayout()
            row.setSpacing(8)
            dot = QLabel("▶")
            dot.setStyleSheet(f"color: {color}; font-size: 8px; background: transparent;")
            row.addWidget(dot)
            s = QLabel(step)
            s.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
            row.addWidget(s)
            row.addStretch()
            v = QLabel(val)
            v.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {color}; background: transparent;")
            row.addWidget(v)
            why_lay.addLayout(row)

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

        # ── Row 3: Counterfactual ─────────────────────────────
        cf_card = Card()
        add_shadow(cf_card)
        cfl = QVBoxLayout(cf_card)
        cfl.setContentsMargins(18, 16, 18, 16)
        cfl.setSpacing(10)
        cf_title = QLabel("Counterfactual Explanation — What Would Change the Prediction?")
        cf_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        cfl.addWidget(cf_title)
        cf_sub = QLabel(
            "To flip the prediction to NORMAL, the following minimum changes would be needed:"
        )
        cf_sub.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        cfl.addWidget(cf_sub)

        cf_grid = QHBoxLayout()
        cf_grid.setSpacing(16)
        counterexamples = [
            ("transaction_amount", "$2,450 → $890", "#ffd400"),
            ("time_of_day",        "02:34AM → 14:00", "#ffd400"),
            ("user_history_score", "0.23 → 0.65",    "#00e0b8"),
        ]
        for feature, change, color in counterexamples:
            ce_w = QWidget()
            ce_w.setStyleSheet(
                f"background: {color}14; border: 1px solid {color}44; border-radius: 10px;"
            )
            ce_lay = QVBoxLayout(ce_w)
            ce_lay.setContentsMargins(14, 12, 14, 12)
            ce_lay.setSpacing(4)
            fname = QLabel(feature)
            fname.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
            fval = QLabel(change)
            fval.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {color}; background: transparent;")
            ce_lay.addWidget(fname)
            ce_lay.addWidget(fval)
            cf_grid.addWidget(ce_w, 1)

        cfl.addLayout(cf_grid)
        lay.addWidget(cf_card)
        lay.addSpacing(10)

    def _connect_engine(self):
        self.engine.shap_updated.connect(self._on_shap)
        self._on_shap(self.engine.snapshot_shap())

    def _on_shap(self, features):
        self._wf_chart.update_features(features)
        self._fi_chart.update_features(features)
        self._shap_bars.set_features(features)
