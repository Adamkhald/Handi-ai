"""
HandiAI — Drift Detection Page
"""

import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QProgressBar
)
from PySide6.QtCore import Qt

import data
from widgets.components import Card, Sparkline, add_shadow


class DriftDetectionPage(QWidget):
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
        t = QLabel("Drift Detection")
        t.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; background: transparent;")
        s = QLabel("Monitor statistical drift across features and models in production")
        s.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        lay.addWidget(t); lay.addWidget(s)

        # ── Overall Drift Status Banner ───────────────────────
        banner = QWidget()
        banner.setStyleSheet(
            "background: rgba(0,201,125,0.1); border: 1px solid #00c97d44; border-radius: 12px;"
        )
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(20, 14, 20, 14)
        bl.setSpacing(16)
        icon = QLabel("✓")
        icon.setStyleSheet("font-size: 24px; color: #00c97d; background: transparent;")
        bl.addWidget(icon)
        col = QVBoxLayout(); col.setSpacing(2)
        bt = QLabel("Overall Drift Status: LOW")
        bt.setStyleSheet("font-size: 14px; font-weight: 700; color: #00c97d; background: transparent;")
        bs = QLabel("No significant drift detected across 12 production models · Last check: 2 min ago")
        bs.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        col.addWidget(bt); col.addWidget(bs)
        bl.addLayout(col); bl.addStretch()
        run_btn = QPushButton("↺  Run Drift Check")
        run_btn.setObjectName("btn_primary")
        run_btn.setFixedHeight(34)
        run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bl.addWidget(run_btn)
        lay.addWidget(banner)

        # ── Per-feature drift table ───────────────────────────
        feat_card = Card()
        add_shadow(feat_card)
        fl = QVBoxLayout(feat_card)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(10)

        fh = QHBoxLayout()
        ft = QLabel("Feature Drift Analysis")
        ft.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        fh.addWidget(ft); fh.addStretch()
        thresh_lbl = QLabel("Threshold: 0.15")
        thresh_lbl.setStyleSheet("font-size: 11px; color: #ffd400; font-weight: 600; background: transparent;")
        fh.addWidget(thresh_lbl)
        fl.addLayout(fh)

        # Header
        hdr = QHBoxLayout()
        for col_name in ["Feature", "PSI Score", "KS Stat", "Drift %", "Status", "Trend"]:
            lbl = QLabel(col_name.upper())
            lbl.setStyleSheet(
                "font-size: 10px; font-weight: 700; color: #5a5888; "
                "letter-spacing: 0.8px; background: transparent;"
            )
            hdr.addWidget(lbl, 2 if col_name == "Feature" else 1)
        fl.addLayout(hdr)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #2e2b5f; max-height: 1px;")
        fl.addWidget(sep)

        features_drift = [
            ("transaction_amount", 0.021, 0.048, 2.1,  "Stable"),
            ("merchant_category",  0.087, 0.123, 8.7,  "Monitor"),
            ("time_of_day",        0.015, 0.031, 1.5,  "Stable"),
            ("location_mismatch",  0.142, 0.187, 14.2, "Warning"),
            ("user_history_score", 0.031, 0.056, 3.1,  "Stable"),
            ("device_fingerprint", 0.009, 0.017, 0.9,  "Stable"),
            ("card_present",       0.053, 0.089, 5.3,  "Monitor"),
        ]

        STATUS_MAP = {
            "Stable":  ("#00c97d", "✓"),
            "Monitor": ("#ffd400", "⚠"),
            "Warning": ("#ff5577", "⚑"),
            "Drift":   ("#ff5577", "⚠"),
        }

        for feat, psi, ks, drift_pct, status in features_drift:
            row = QHBoxLayout()
            row.setSpacing(0)

            name = QLabel(feat)
            name.setStyleSheet("font-size: 12px; font-weight: 600; color: #e0dff5; background: transparent;")
            row.addWidget(name, 2)

            sc, si = STATUS_MAP[status]
            psi_lbl = QLabel(f"{psi:.3f}")
            psi_lbl.setStyleSheet(f"font-size: 11px; color: {sc}; font-weight: 600; background: transparent;")
            row.addWidget(psi_lbl, 1)

            ks_lbl = QLabel(f"{ks:.3f}")
            ks_lbl.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
            row.addWidget(ks_lbl, 1)

            dp_lbl = QLabel(f"{drift_pct:.1f}%")
            dp_lbl.setStyleSheet(f"font-size: 11px; color: {sc}; font-weight: 700; background: transparent;")
            row.addWidget(dp_lbl, 1)

            st_badge = QLabel(f"{si}  {status}")
            st_badge.setStyleSheet(
                f"background: {sc}22; border: 1px solid {sc}44; border-radius: 8px; "
                f"color: {sc}; font-size: 10px; font-weight: 700; padding: 2px 8px;"
            )
            row.addWidget(st_badge, 1)

            # Sparkline trend
            trend_data = [random.uniform(0.01, drift_pct/100 + 0.05) for _ in range(12)]
            spark = Sparkline(trend_data, color=sc, fill=True)
            spark.setFixedSize(80, 28)
            row.addWidget(spark, 1)

            fl.addLayout(row)

            if feat != features_drift[-1][0]:
                sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
                sep2.setStyleSheet("background: #2a2855; max-height: 1px;")
                fl.addWidget(sep2)

        lay.addWidget(feat_card)

        # ── Per-model drift overview ───────────────────────────
        model_card = Card()
        add_shadow(model_card)
        ml = QVBoxLayout(model_card)
        ml.setContentsMargins(20, 16, 20, 16)
        ml.setSpacing(10)

        mth = QLabel("Model-Level Drift Scores")
        mth.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        ml.addWidget(mth)

        self._model_drift_bars = {}
        self._model_drift_labels = {}

        for model in data.MODELS[:8]:
            drift_val = model["drift"]
            color = "#00c97d" if drift_val < 0.05 else ("#ffd400" if drift_val < 0.12 else "#ff5577")
            row = QHBoxLayout()
            row.setSpacing(12)

            nm = QLabel(model["name"])
            nm.setFixedWidth(200)
            nm.setStyleSheet("font-size: 12px; color: #e0dff5; background: transparent;")
            row.addWidget(nm)

            bar = QProgressBar()
            bar.setValue(int(drift_val * 1000))
            bar.setMaximum(300)
            bar.setFixedHeight(8)
            bar.setTextVisible(False)
            bar.setStyleSheet(
                f"QProgressBar {{ background: #2e2b5f; border-radius: 4px; border: none; }}"
                f"QProgressBar::chunk {{ background: {color}; border-radius: 4px; }}"
            )
            row.addWidget(bar, 1)
            self._model_drift_bars[model["name"]] = bar

            drift_lbl = QLabel(f"{drift_val:.2f}")
            drift_lbl.setFixedWidth(50)
            drift_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            drift_lbl.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: 700; background: transparent;")
            row.addWidget(drift_lbl)
            self._model_drift_labels[model["name"]] = drift_lbl

            ml.addLayout(row)

        lay.addWidget(model_card)
        lay.addSpacing(10)

    def _connect_engine(self):
        self.engine.model_drift_updated.connect(self._on_model_drift)

    def _on_model_drift(self, drifts):
        for name, val in drifts:
            if name in self._model_drift_bars:
                bar = self._model_drift_bars[name]
                lbl = self._model_drift_labels[name]
                
                color = "#00c97d" if val < 0.05 else ("#ffd400" if val < 0.12 else "#ff5577")
                bar.setStyleSheet(
                    f"QProgressBar {{ background: #2e2b5f; border-radius: 4px; border: none; }}"
                    f"QProgressBar::chunk {{ background: {color}; border-radius: 4px; }}"
                )
                bar.setValue(int(val * 1000))
                
                lbl.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: 700; background: transparent;")
                lbl.setText(f"{val:.3f}")

