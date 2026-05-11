"""
HandiAI — Dashboard Page (Main landing page)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QTimer

import data
from widgets.components import (
    Card, MetricCard, CircularGauge, Sparkline, DonutChart, make_label, add_shadow
)
from charts.matplotlib_charts import (
    ProductionChart, TrafficChart, DriftMiniChart
)


# ─────────────────────────────────────────────────────────────
#  Section Title Helper
# ─────────────────────────────────────────────────────────────
def section_title(text, subtitle=""):
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(2)
    t = QLabel(text)
    t.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff; background: transparent;")
    lay.addWidget(t)
    if subtitle:
        s = QLabel(subtitle)
        s.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        lay.addWidget(s)
    return w


# ─────────────────────────────────────────────────────────────
#  SHAP Donut Card
# ─────────────────────────────────────────────────────────────
class SHAPDonutCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("SHAP Feature Contribution")
        title.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        header.addWidget(title)
        header.addStretch()
        btn = QPushButton("Details →")
        btn.setObjectName("btn_secondary")
        btn.setFixedHeight(26)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header.addWidget(btn)
        lay.addLayout(header)

        # Donut + legend row
        content = QHBoxLayout()
        content.setSpacing(12)

        self._donut = DonutChart(data.SHAP_DONUT_DATA)
        self._donut.setFixedSize(100, 100)
        content.addWidget(self._donut)

        legend_col = QVBoxLayout()
        legend_col.setSpacing(4)
        for label, pct, color in data.SHAP_DONUT_DATA:
            row = QHBoxLayout()
            row.setSpacing(6)
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 10px; background: transparent;")
            row.addWidget(dot)
            lbl = QLabel(f"{label[:16]}")
            lbl.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
            row.addWidget(lbl)
            row.addStretch()
            pct_lbl = QLabel(f"{pct}%")
            pct_lbl.setStyleSheet("font-size: 10px; font-weight: 700; color: #ffffff; background: transparent;")
            row.addWidget(pct_lbl)
            legend_col.addLayout(row)
        content.addLayout(legend_col)
        lay.addLayout(content)


# ─────────────────────────────────────────────────────────────
#  Traffic Card
# ─────────────────────────────────────────────────────────────
class TrafficCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 10)
        lay.setSpacing(6)

        header = QHBoxLayout()
        title = QLabel("Traffic & Requests")
        title.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        header.addWidget(title)
        header.addStretch()
        badge = QLabel("● LIVE")
        badge.setStyleSheet("color: #00c97d; font-size: 10px; font-weight: 700; background: transparent;")
        header.addWidget(badge)
        lay.addLayout(header)

        value_row = QHBoxLayout()
        self._val_lbl = QLabel("1.2M")
        self._val_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #00e0b8; background: transparent;")
        value_row.addWidget(self._val_lbl)
        sub = QLabel("requests / day")
        sub.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
        value_row.addWidget(sub, alignment=Qt.AlignmentFlag.AlignBottom)
        value_row.addStretch()
        lay.addLayout(value_row)

        self._chart = TrafficChart()
        self._chart.setFixedHeight(60)
        lay.addWidget(self._chart)


# ─────────────────────────────────────────────────────────────
#  Drift Score Card
# ─────────────────────────────────────────────────────────────
class DriftScoreCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 10)
        lay.setSpacing(6)

        header = QHBoxLayout()
        title = QLabel("Model Drift Score")
        title.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        header.addWidget(title)
        header.addStretch()
        alert = QLabel("⚠ Stable")
        alert.setStyleSheet("color: #ffd400; font-size: 10px; font-weight: 700; background: transparent;")
        header.addWidget(alert)
        lay.addLayout(header)

        value_row = QHBoxLayout()
        self._val_lbl = QLabel("2.4%")
        self._val_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #b46cff; background: transparent;")
        value_row.addWidget(self._val_lbl)
        sub = QLabel("avg drift score")
        sub.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
        value_row.addWidget(sub, alignment=Qt.AlignmentFlag.AlignBottom)
        value_row.addStretch()
        lay.addLayout(value_row)

        self._chart = DriftMiniChart()
        self._chart.setFixedHeight(50)
        lay.addWidget(self._chart)


# ─────────────────────────────────────────────────────────────
#  Model Confidence Gauge Card
# ─────────────────────────────────────────────────────────────
class GaugeCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        title = QLabel("Model Confidence")
        title.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        lay.addWidget(title)

        sub = QLabel("fraud_detector_v3 · XGBoost")
        sub.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
        lay.addWidget(sub)

        self._gauge = CircularGauge(92, "Confidence Score")
        self._gauge.setMinimumSize(180, 180)
        lay.addWidget(self._gauge, alignment=Qt.AlignmentFlag.AlignCenter)

        # Controls
        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)
        for label, icon in [("Prev", "◀"), ("Refresh", "↺"), ("Next", "▶")]:
            btn = QPushButton(f"{icon}  {label}")
            btn.setObjectName("btn_secondary")
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            ctrl.addWidget(btn)
        lay.addLayout(ctrl)


# ─────────────────────────────────────────────────────────────
#  Right Large Graph Panel
# ─────────────────────────────────────────────────────────────
class ProductionChartCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("Production Predictions Monitoring")
        title.setStyleSheet("font-size: 14px; font-weight: 700; color: #ffffff; background: transparent;")
        sub = QLabel("Confidence % and Drift Score over the last 30 days")
        sub.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
        title_col.addWidget(title)
        title_col.addWidget(sub)
        header.addLayout(title_col)
        header.addStretch()

        # Period selector
        for period in ["7D", "30D", "90D"]:
            btn = QPushButton(period)
            btn.setFixedSize(40, 26)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                "QPushButton { background: rgba(180,108,255,0.15); border: 1px solid #b46cff44; "
                "border-radius: 8px; color: #b46cff; font-size: 11px; font-weight: 600; }"
                "QPushButton:hover { background: rgba(180,108,255,0.3); }"
            )
            header.addWidget(btn)

        lay.addLayout(header)

        # Legend row
        legend = QHBoxLayout()
        for color, label in [("#00e0b8", "Confidence %"), ("#b46cff", "Drift Score")]:
            row = QHBoxLayout()
            row.setSpacing(6)
            dot = QLabel("━")
            dot.setStyleSheet(f"color: {color}; font-size: 14px; background: transparent;")
            row.addWidget(dot)
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
            row.addWidget(lbl)
            legend.addLayout(row)
            legend.addSpacing(16)
        legend.addStretch()
        lay.addLayout(legend)

        # Chart
        self._chart = ProductionChart()
        lay.addWidget(self._chart)


# ─────────────────────────────────────────────────────────────
#  Dashboard Page
# ─────────────────────────────────────────────────────────────
class DashboardPage(QWidget):
    def __init__(self, engine=None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setObjectName("page_container")
        self._setup_ui()
        if self.engine:
            self._connect_engine()

    def _setup_ui(self):
        # Outer scroll area
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

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

        # ── Page header ──────────────────────────────────────
        ph = QHBoxLayout()
        pg_title = QLabel("Dashboard")
        pg_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; background: transparent;")
        pg_sub = QLabel("Explainable AI Operations Center  ·  Last updated: just now")
        pg_sub.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        ph_col = QVBoxLayout()
        ph_col.setSpacing(2)
        ph_col.addWidget(pg_title)
        ph_col.addWidget(pg_sub)
        ph.addLayout(ph_col)
        ph.addStretch()
        btn_refresh = QPushButton("↺  Refresh")
        btn_refresh.setObjectName("btn_primary")
        btn_refresh.setFixedHeight(36)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        ph.addWidget(btn_refresh)
        lay.addLayout(ph)

        # ── Row 1: Summary Metric Cards ───────────────────────
        metric_row = QHBoxLayout()
        metric_row.setSpacing(16)
        
        self._metric_cards = []
        fmt_fns = [
            lambda v: str(int(v)),
            lambda v: f"{v:.1f}%",
            None, # requests is string format already from engine
            None  # drift uses string format from engine too or custom, let's keep it direct
        ]
        
        for i, m in enumerate(data.SUMMARY_METRICS):
            fmt = fmt_fns[i] if i < len(fmt_fns) else None
            card = MetricCard(m["title"], m["value"], m["trend"], m["icon"], m["color"], fmt_fn=fmt)
            add_shadow(card, blur=20, y_off=4)
            metric_row.addWidget(card)
            self._metric_cards.append(card)
        lay.addLayout(metric_row)

        # ── Row 2: Gauge | Center Cards | Big Chart ───────────
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        # Left — Gauge
        self._gauge_card = GaugeCard()
        self._gauge_card.setFixedWidth(270)
        add_shadow(self._gauge_card)
        row2.addWidget(self._gauge_card)

        # Centre — Stacked cards
        center_col = QVBoxLayout()
        center_col.setSpacing(12)
        self._shap_card  = SHAPDonutCard()
        add_shadow(self._shap_card)
        center_col.addWidget(self._shap_card)

        self._traffic_card = TrafficCard()
        add_shadow(self._traffic_card)
        center_col.addWidget(self._traffic_card)

        self._drift_card = DriftScoreCard()
        add_shadow(self._drift_card)
        center_col.addWidget(self._drift_card)

        center_w = QWidget()
        center_w.setStyleSheet("background: transparent;")
        center_w.setLayout(center_col)
        center_w.setFixedWidth(280)
        row2.addWidget(center_w)

        # Right — Big chart
        self._prod_card = ProductionChartCard()
        add_shadow(self._prod_card)
        row2.addWidget(self._prod_card, 1)
        lay.addLayout(row2)

        # ── Row 3: Quick Model Status Table ──────────────────
        models_card = Card()
        add_shadow(models_card)
        mc_lay = QVBoxLayout(models_card)
        mc_lay.setContentsMargins(16, 14, 16, 14)
        mc_lay.setSpacing(12)

        mh = QHBoxLayout()
        t = QLabel("Active Models Overview")
        t.setStyleSheet("font-size: 14px; font-weight: 700; color: #ffffff; background: transparent;")
        mh.addWidget(t)
        mh.addStretch()
        btn_all = QPushButton("View All Models →")
        btn_all.setObjectName("btn_secondary")
        btn_all.setFixedHeight(28)
        btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        mh.addWidget(btn_all)
        mc_lay.addLayout(mh)

        # Mini table header
        hdr = QHBoxLayout()
        for col in ["Model Name", "Type", "Accuracy", "Drift", "Status", "Requests"]:
            lbl = QLabel(col.upper())
            lbl.setStyleSheet(
                "font-size: 10px; font-weight: 700; color: #5a5888; "
                "letter-spacing: 0.8px; background: transparent;"
            )
            hdr.addWidget(lbl, 1 if col != "Model Name" else 2)
        mc_lay.addLayout(hdr)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #2e2b5f; max-height: 1px;")
        mc_lay.addWidget(sep)

        # Rows (show top 6 — populated when real data is loaded)
        if not data.MODELS:
            empty = QLabel("No models loaded — use Upload & Analyze to add your first model.")
            empty.setStyleSheet(
                "font-size: 12px; color: #5a5888; padding: 16px 0; background: transparent;"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            mc_lay.addWidget(empty)
        else:
            STATUS_COLORS = {
                "Production": "#00c97d", "Staging": "#ffd400",
                "Testing": "#4d9fff",   "Retired": "#ff5577",
            }
            for i, model in enumerate(data.MODELS[:6]):
                row = QHBoxLayout(); row.setSpacing(0)

                name_lbl = QLabel(model["name"])
                name_lbl.setStyleSheet("font-size: 12px; color: #ffffff; font-weight: 600; background: transparent;")
                row.addWidget(name_lbl, 2)

                type_lbl = QLabel(model["type"])
                type_lbl.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
                row.addWidget(type_lbl, 1)

                acc_lbl = QLabel(f"{model['accuracy']:.1f}%")
                acc_lbl.setStyleSheet("font-size: 11px; color: #00e0b8; font-weight: 600; background: transparent;")
                row.addWidget(acc_lbl, 1)

                drift_v = model["drift"]
                drift_color = "#00c97d" if drift_v < 0.05 else ("#ffd400" if drift_v < 0.12 else "#ff5577")
                drift_lbl = QLabel(f"{drift_v:.2f}")
                drift_lbl.setStyleSheet(f"font-size: 11px; color: {drift_color}; font-weight: 600; background: transparent;")
                row.addWidget(drift_lbl, 1)

                st_color = STATUS_COLORS.get(model["status"], "#9896c8")
                status_container = QWidget()
                status_container.setStyleSheet(
                    f"background: {st_color}22; border-radius: 8px; border: 1px solid {st_color}44;"
                )
                st_inner = QHBoxLayout(status_container)
                st_inner.setContentsMargins(8, 2, 8, 2)
                st_lbl = QLabel(model["status"])
                st_lbl.setStyleSheet(f"font-size: 10px; color: {st_color}; font-weight: 700; background: transparent;")
                st_inner.addWidget(st_lbl)
                row.addWidget(status_container, 1)

                reqs = model["requests"]
                req_str = (f"{reqs/1_000_000:.1f}M" if reqs >= 1_000_000
                           else f"{reqs/1000:.0f}K" if reqs >= 1000 else str(reqs) or "—")
                req_lbl = QLabel(req_str)
                req_lbl.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
                row.addWidget(req_lbl, 1)

                mc_lay.addLayout(row)

                if i < len(data.MODELS[:6]) - 1:
                    sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
                    sep2.setStyleSheet("background: #2a2855; max-height: 1px;")
                    mc_lay.addWidget(sep2)

        lay.addWidget(models_card)
        lay.addSpacing(10)

    def _connect_engine(self):
        self.engine.metrics_updated.connect(self._on_metrics)
        self.engine.gauge_updated.connect(self._gauge_card._gauge.set_value)
        self.engine.traffic_updated.connect(self._traffic_card._chart.update_data)
        self.engine.drift_mini_updated.connect(self._drift_card._chart.update_data)
        self.engine.chart_updated.connect(self._prod_card._chart.update_data)
        self.engine.shap_updated.connect(self._on_shap)

    def _on_metrics(self, models, acc, req_str, drift, instant=False):
        if len(self._metric_cards) == 4:
            self._metric_cards[0].set_value(models, "+0 this week", instant)
            self._metric_cards[1].set_value(acc, "+0.1% vs last", instant)
            self._metric_cards[2].set_value(req_str, "~ Live", instant)
            
            # format drift score
            ds_str = f"{drift:.1f}%" if drift < 5 else f"{drift:.1f}% (!)"
            self._metric_cards[3].set_value(ds_str, "Updating...", instant)
            
        self._traffic_card._val_lbl.setText(req_str)
        self._drift_card._val_lbl.setText(f"{drift:.1f}%")

    def _on_shap(self, features):
        # Build donut data from top 4 positive features
        pos = [f for f in features if f["direction"] == "positive"]
        pos.sort(key=lambda x: x["shap"], reverse=True)
        top = pos[:3]
        total = sum(f["shap"] for f in features)
        if total == 0: total = 1
        
        segs = []
        colors = ["#b46cff", "#00e0b8", "#ffd400", "#ff5577"]
        for i, f in enumerate(top):
            pct = int((f["shap"]/total)*100)
            segs.append((f["name"], pct, colors[i%len(colors)]))
        
        rem = 100 - sum(s[1] for s in segs)
        if rem > 0:
            segs.append(("Other Features", rem, "#4d9fff"))
            
        self._shap_card._donut.set_segments(segs)
