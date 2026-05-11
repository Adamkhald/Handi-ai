"""
HandiAI — Dashboard Page
"""

import json
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QRunnable, QThreadPool, QObject, Signal

import data
from widgets.components import (
    Card, MetricCard, CircularGauge, DonutChart, make_label, add_shadow
)
from charts.matplotlib_charts import (
    ProductionChart, TrafficChart, DriftMiniChart
)

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = "sk-f85cff66dd3a4dd6a0bafef945b6ddfc"
DEEPSEEK_URL     = "https://api.deepseek.com/v1/chat/completions"


# ─────────────────────────────────────────────────────────────
#  DeepSeek Worker
# ─────────────────────────────────────────────────────────────
class _DeepSeekSignals(QObject):
    done  = Signal(str)
    error = Signal(str)


class _DeepSeekWorker(QRunnable):
    def __init__(self, messages):
        super().__init__()
        self.messages = messages
        self.signals  = _DeepSeekSignals()

    def run(self):
        try:
            import urllib.request
            payload = json.dumps({
                "model":    "deepseek-chat",
                "messages": self.messages,
                "max_tokens": 300,
            }).encode("utf-8")
            req = urllib.request.Request(
                DEEPSEEK_URL,
                data    = payload,
                headers = {
                    "Content-Type":  "application/json",
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                },
                method = "POST",
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            text = body["choices"][0]["message"]["content"].strip()
            self.signals.done.emit(text)
        except Exception as e:
            self.signals.error.emit(f"(API error: {e})")

# ─────────────────────────────────────────────────────────────
#  Chat Components
# ─────────────────────────────────────────────────────────────
class ChatBubble(QWidget):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(0)

        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(220)

        if is_user:
            bubble.setStyleSheet(
                "background: #111111; color: #ffffff; border-radius: 10px; "
                "padding: 7px 11px; font-size: 12px;"
            )
            lay.addStretch()
            lay.addWidget(bubble)
        else:
            bubble.setStyleSheet(
                "background: #f0f0f0; color: #111111; border-radius: 10px; "
                "padding: 7px 11px; font-size: 12px;"
            )
            lay.addWidget(bubble)
            lay.addStretch()


class ChatPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFixedSize(300, 420)
        self._pool    = QThreadPool()
        self._history = [
            {"role": "system", "content": (
                "You are HandiAI Assistant, an expert in ML model monitoring, "
                "drift detection, SHAP explainability, and MLOps. "
                "Answer concisely (2-4 sentences max). "
                "If asked about the current dashboard, say data updates live."
            )}
        ]
        self._setup_ui()
        self.hide()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        header = QWidget()
        header.setStyleSheet("background: #111111; border-radius: 12px 12px 0 0;")
        header.setFixedHeight(46)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(14, 0, 14, 0)
        title = QLabel("HandiAI Assistant")
        title.setStyleSheet(
            "color: #ffffff; font-size: 13px; font-weight: 700; background: transparent;"
        )
        hl.addWidget(title)
        hl.addStretch()
        status = QLabel("DeepSeek")
        status.setStyleSheet("color: #888888; font-size: 10px; background: transparent;")
        hl.addWidget(status)
        lay.addWidget(header)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { background: #ffffff; border: none; }")

        self._msg_widget = QWidget()
        self._msg_widget.setStyleSheet("background: #ffffff;")
        self._msg_lay = QVBoxLayout(self._msg_widget)
        self._msg_lay.setContentsMargins(12, 12, 12, 12)
        self._msg_lay.setSpacing(4)
        self._msg_lay.addStretch()
        self._scroll.setWidget(self._msg_widget)
        lay.addWidget(self._scroll, 1)

        input_row = QWidget()
        input_row.setStyleSheet(
            "background: #f8f8f8; border-top: 1px solid #e8e8e8; border-radius: 0 0 12px 12px;"
        )
        input_row.setFixedHeight(52)
        ir = QHBoxLayout(input_row)
        ir.setContentsMargins(12, 8, 12, 8)
        ir.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask about your models...")
        self._input.setStyleSheet(
            "QLineEdit { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; "
            "padding: 6px 10px; font-size: 12px; color: #111111; }"
        )
        self._input.returnPressed.connect(self._send)
        ir.addWidget(self._input)

        self._send_btn = QPushButton("Send")
        self._send_btn.setFixedSize(52, 32)
        self._send_btn.setStyleSheet(
            "QPushButton { background: #111111; color: #ffffff; border-radius: 8px; "
            "font-size: 12px; font-weight: 600; border: none; }"
            "QPushButton:hover { background: #333333; }"
            "QPushButton:disabled { background: #cccccc; }"
        )
        self._send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._send_btn.clicked.connect(self._send)
        ir.addWidget(self._send_btn)
        lay.addWidget(input_row)

        self._add_message(
            "Hello! I'm powered by DeepSeek. Ask me about your models, drift, SHAP, or anything ML.", False
        )

    def _add_message(self, text, is_user):
        bubble = ChatBubble(text, is_user)
        self._msg_lay.insertWidget(self._msg_lay.count() - 1, bubble)
        QTimer.singleShot(60, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))
        return bubble

    def _send(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._input.setEnabled(False)
        self._send_btn.setEnabled(False)
        self._add_message(text, True)

        # Show thinking indicator
        thinking = self._add_message("Thinking…", False)

        # Build message history
        self._history.append({"role": "user", "content": text})
        messages = list(self._history)

        worker = _DeepSeekWorker(messages)
        worker.signals.done.connect(lambda reply: self._on_reply(thinking, reply))
        worker.signals.error.connect(lambda err: self._on_reply(thinking, err))
        self._pool.start(worker)

    def _on_reply(self, thinking_bubble, text):
        # Remove the thinking bubble
        idx = self._msg_lay.indexOf(thinking_bubble)
        if idx >= 0:
            self._msg_lay.takeAt(idx)
            thinking_bubble.deleteLater()

        # Add real reply
        self._history.append({"role": "assistant", "content": text})
        self._add_message(text, False)

        self._input.setEnabled(True)
        self._send_btn.setEnabled(True)
        self._input.setFocus()


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
        title.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #000000; background: transparent;"
        )
        header.addWidget(title)
        header.addStretch()
        self._details_btn = QPushButton("Details")
        self._details_btn.setObjectName("btn_secondary")
        self._details_btn.setFixedHeight(26)
        self._details_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header.addWidget(self._details_btn)
        lay.addLayout(header)

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
            dot = QWidget()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(f"background: {color}; border-radius: 4px;")
            row.addWidget(dot, alignment=Qt.AlignmentFlag.AlignVCenter)
            lbl = QLabel(f"{label[:16]}")
            lbl.setStyleSheet("font-size: 10px; color: #888888; background: transparent;")
            row.addWidget(lbl)
            row.addStretch()
            pct_lbl = QLabel(f"{pct}%")
            pct_lbl.setStyleSheet(
                "font-size: 10px; font-weight: 700; color: #000000; background: transparent;"
            )
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
        title.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #000000; background: transparent;"
        )
        header.addWidget(title)
        header.addStretch()
        badge = QLabel("LIVE")
        badge.setStyleSheet(
            "color: #555555; font-size: 10px; font-weight: 700; background: transparent;"
        )
        header.addWidget(badge)
        lay.addLayout(header)

        value_row = QHBoxLayout()
        self._val_lbl = QLabel("—")
        self._val_lbl.setStyleSheet(
            "font-size: 20px; font-weight: 800; color: #222222; background: transparent;"
        )
        value_row.addWidget(self._val_lbl)
        sub = QLabel("requests / day")
        sub.setStyleSheet("font-size: 10px; color: #888888; background: transparent;")
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
        title.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #000000; background: transparent;"
        )
        header.addWidget(title)
        header.addStretch()
        alert = QLabel("Stable")
        alert.setStyleSheet(
            "color: #888888; font-size: 10px; font-weight: 700; background: transparent;"
        )
        header.addWidget(alert)
        lay.addLayout(header)

        value_row = QHBoxLayout()
        self._val_lbl = QLabel("—")
        self._val_lbl.setStyleSheet(
            "font-size: 20px; font-weight: 800; color: #000000; background: transparent;"
        )
        value_row.addWidget(self._val_lbl)
        sub = QLabel("avg drift score")
        sub.setStyleSheet("font-size: 10px; color: #888888; background: transparent;")
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
        title.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #000000; background: transparent;"
        )
        lay.addWidget(title)

        sub = QLabel("fraud_detector_v3  XGBoost")
        sub.setStyleSheet("font-size: 10px; color: #888888; background: transparent;")
        lay.addWidget(sub)

        self._gauge = CircularGauge(92, "Confidence Score")
        self._gauge.setMinimumSize(180, 180)
        lay.addWidget(self._gauge, alignment=Qt.AlignmentFlag.AlignCenter)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)
        for label in ["Prev", "Refresh", "Next"]:
            btn = QPushButton(label)
            btn.setObjectName("btn_secondary")
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            ctrl.addWidget(btn)
        lay.addLayout(ctrl)


# ─────────────────────────────────────────────────────────────
#  Production Chart Card
# ─────────────────────────────────────────────────────────────
class ProductionChartCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("Production Predictions Monitoring")
        title.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #000000; background: transparent;"
        )
        sub = QLabel("Confidence % and Drift Score over the last 30 days")
        sub.setStyleSheet("font-size: 10px; color: #888888; background: transparent;")
        title_col.addWidget(title)
        title_col.addWidget(sub)
        header.addLayout(title_col)
        header.addStretch()

        for period in ["7D", "30D", "90D"]:
            btn = QPushButton(period)
            btn.setFixedSize(40, 26)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                "QPushButton { background: #f0f0f0; border: 1px solid #d8d8d8; "
                "border-radius: 8px; color: #333333; font-size: 11px; font-weight: 600; }"
                "QPushButton:hover { background: #e8e8e8; }"
            )
            header.addWidget(btn)
        lay.addLayout(header)

        legend = QHBoxLayout()
        for color, label in [("#555555", "Confidence %"), ("#333333", "Drift Score")]:
            row = QHBoxLayout()
            row.setSpacing(6)
            line = QFrame()
            line.setFixedSize(16, 3)
            line.setStyleSheet(f"background: {color}; border-radius: 1px;")
            row.addWidget(line, alignment=Qt.AlignmentFlag.AlignVCenter)
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
            row.addWidget(lbl)
            legend.addLayout(row)
            legend.addSpacing(16)
        legend.addStretch()
        lay.addLayout(legend)

        self._chart = ProductionChart()
        lay.addWidget(self._chart)


# ─────────────────────────────────────────────────────────────
#  Dashboard Page
# ─────────────────────────────────────────────────────────────
class DashboardPage(QWidget):
    def __init__(self, engine=None, navigate_fn=None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._navigate = navigate_fn
        self.setObjectName("page_container")
        self._setup_ui()
        if self.engine:
            self._connect_engine()

    def _setup_ui(self):
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

        # Page header
        ph = QHBoxLayout()
        pg_title = QLabel("Dashboard")
        pg_title.setStyleSheet(
            "font-size: 22px; font-weight: 800; color: #000000; background: transparent;"
        )
        pg_sub = QLabel("Explainable AI Operations Center  ·  Last updated: just now")
        pg_sub.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
        ph_col = QVBoxLayout()
        ph_col.setSpacing(2)
        ph_col.addWidget(pg_title)
        ph_col.addWidget(pg_sub)
        ph.addLayout(ph_col)
        ph.addStretch()
        btn_refresh = QPushButton("Refresh")
        btn_refresh.setObjectName("btn_primary")
        btn_refresh.setFixedHeight(36)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(lambda: self.engine and self._connect_engine())
        ph.addWidget(btn_refresh)
        lay.addLayout(ph)

        # Row 1: Summary Metric Cards
        metric_row = QHBoxLayout()
        metric_row.setSpacing(16)

        self._metric_cards = []
        fmt_fns = [
            lambda v: str(int(v)),
            lambda v: f"{v:.1f}%",
            None,
            None,
        ]
        nav_targets = [2, 4, 5, 4]  # Models, Monitoring, Logs, Monitoring

        for i, m in enumerate(data.SUMMARY_METRICS):
            fmt = fmt_fns[i] if i < len(fmt_fns) else None
            target = nav_targets[i]
            on_click = (lambda t=target: self._navigate and self._navigate(t))
            card = MetricCard(
                m["title"], m["value"], m["trend"], m["icon"], m["color"],
                fmt_fn=fmt, on_click=on_click,
            )
            add_shadow(card, blur=20, y_off=4)
            metric_row.addWidget(card)
            self._metric_cards.append(card)
        lay.addLayout(metric_row)

        # Row 2: Gauge | Center Cards | Big Chart
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        self._gauge_card = GaugeCard()
        self._gauge_card.setFixedWidth(270)
        add_shadow(self._gauge_card)
        row2.addWidget(self._gauge_card)

        center_col = QVBoxLayout()
        center_col.setSpacing(12)

        self._shap_card = SHAPDonutCard()
        add_shadow(self._shap_card)
        self._shap_card._details_btn.clicked.connect(
            lambda: self._navigate and self._navigate(3))
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

        self._prod_card = ProductionChartCard()
        add_shadow(self._prod_card)
        row2.addWidget(self._prod_card, 1)
        lay.addLayout(row2)

        # Row 3: Active Models Table
        models_card = Card()
        add_shadow(models_card)
        mc_lay = QVBoxLayout(models_card)
        mc_lay.setContentsMargins(16, 14, 16, 14)
        mc_lay.setSpacing(12)

        mh = QHBoxLayout()
        t = QLabel("Active Models Overview")
        t.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #000000; background: transparent;"
        )
        mh.addWidget(t)
        mh.addStretch()
        btn_all = QPushButton("View All Models")
        btn_all.setObjectName("btn_secondary")
        btn_all.setFixedHeight(28)
        btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_all.clicked.connect(lambda: self._navigate and self._navigate(2))
        mh.addWidget(btn_all)
        mc_lay.addLayout(mh)

        hdr = QHBoxLayout()
        for col in ["Model Name", "Type", "Accuracy", "Drift", "Status", "Requests"]:
            lbl = QLabel(col.upper())
            lbl.setStyleSheet(
                "font-size: 10px; font-weight: 700; color: #444444; "
                "letter-spacing: 0.8px; background: transparent;"
            )
            hdr.addWidget(lbl, 1 if col != "Model Name" else 2)
        mc_lay.addLayout(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #e0e0e0; max-height: 1px;")
        mc_lay.addWidget(sep)

        if not data.MODELS:
            empty = QLabel("No models loaded — use Upload & Analyze to add your first model.")
            empty.setStyleSheet(
                "font-size: 12px; color: #444444; padding: 16px 0; background: transparent;"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            mc_lay.addWidget(empty)
        else:
            STATUS_COLORS = {
                "Production": "#aaaaaa", "Staging": "#888888",
                "Testing": "#aaaaaa",    "Retired": "#888888",
            }
            for i, model in enumerate(data.MODELS[:6]):
                row = QHBoxLayout()
                row.setSpacing(0)

                name_lbl = QLabel(model["name"])
                name_lbl.setStyleSheet(
                    "font-size: 12px; color: #000000; font-weight: 600; background: transparent;"
                )
                row.addWidget(name_lbl, 2)

                type_lbl = QLabel(model["type"])
                type_lbl.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
                row.addWidget(type_lbl, 1)

                acc_lbl = QLabel(f"{model['accuracy']:.1f}%")
                acc_lbl.setStyleSheet(
                    "font-size: 11px; color: #222222; font-weight: 600; background: transparent;"
                )
                row.addWidget(acc_lbl, 1)

                drift_v = model["drift"]
                drift_color = "#aaaaaa" if drift_v < 0.05 else ("#888888" if drift_v < 0.12 else "#333333")
                drift_lbl = QLabel(f"{drift_v:.2f}")
                drift_lbl.setStyleSheet(
                    f"font-size: 11px; color: {drift_color}; font-weight: 600; background: transparent;"
                )
                row.addWidget(drift_lbl, 1)

                st_color = STATUS_COLORS.get(model["status"], "#888888")
                status_container = QWidget()
                status_container.setStyleSheet(
                    f"background: {st_color}22; border-radius: 8px; border: 1px solid {st_color}44;"
                )
                st_inner = QHBoxLayout(status_container)
                st_inner.setContentsMargins(8, 2, 8, 2)
                st_lbl = QLabel(model["status"])
                st_lbl.setStyleSheet(
                    f"font-size: 10px; color: {st_color}; font-weight: 700; background: transparent;"
                )
                st_inner.addWidget(st_lbl)
                row.addWidget(status_container, 1)

                reqs = model["requests"]
                req_str = (
                    f"{reqs / 1_000_000:.1f}M" if reqs >= 1_000_000
                    else f"{reqs / 1000:.0f}K" if reqs >= 1000
                    else str(reqs) or "—"
                )
                req_lbl = QLabel(req_str)
                req_lbl.setStyleSheet("font-size: 11px; color: #888888; background: transparent;")
                row.addWidget(req_lbl, 1)

                mc_lay.addLayout(row)

                if i < len(data.MODELS[:6]) - 1:
                    sep2 = QFrame()
                    sep2.setFrameShape(QFrame.Shape.HLine)
                    sep2.setStyleSheet("background: #e0e0e0; max-height: 1px;")
                    mc_lay.addWidget(sep2)

        lay.addWidget(models_card)
        lay.addSpacing(10)

        # Floating chat overlay (children of self, positioned via resizeEvent)
        self._chat_panel = ChatPanel(self)
        self._chat_btn = QPushButton("Ask AI", self)
        self._chat_btn.setFixedSize(80, 36)
        self._chat_btn.setStyleSheet(
            "QPushButton { background: #111111; color: #ffffff; border-radius: 18px; "
            "font-size: 12px; font-weight: 600; border: none; }"
            "QPushButton:hover { background: #333333; }"
        )
        self._chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._chat_btn.clicked.connect(self._toggle_chat)
        self._chat_btn.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_chat()

    def _position_chat(self):
        margin = 24
        bw = self._chat_btn.width()
        bh = self._chat_btn.height()
        pw = self._chat_panel.width()
        ph = self._chat_panel.height()

        bx = self.width() - bw - margin
        by = self.height() - bh - margin
        self._chat_btn.move(bx, by)

        px = self.width() - pw - margin
        py = by - ph - 8
        self._chat_panel.move(px, py)

    def _toggle_chat(self):
        self._chat_panel.setVisible(not self._chat_panel.isVisible())
        self._position_chat()
        if self._chat_panel.isVisible():
            self._chat_panel.raise_()
            self._chat_panel._input.setFocus()
        self._chat_btn.raise_()

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
            ds_str = f"{drift:.1f}%" if drift < 5 else f"{drift:.1f}% (!)"
            self._metric_cards[3].set_value(ds_str, "Updating...", instant)
        self._traffic_card._val_lbl.setText(req_str)
        self._drift_card._val_lbl.setText(f"{drift:.1f}%")

    def _on_shap(self, features):
        pos = [f for f in features if f["direction"] == "positive"]
        pos.sort(key=lambda x: x["shap"], reverse=True)
        top = pos[:3]
        total = sum(f["shap"] for f in features)
        if total == 0:
            total = 1

        segs = []
        colors = ["#222222", "#555555", "#888888", "#aaaaaa"]
        for i, f in enumerate(top):
            pct = int((f["shap"] / total) * 100)
            segs.append((f["name"], pct, colors[i % len(colors)]))

        rem = 100 - sum(s[1] for s in segs)
        if rem > 0:
            segs.append(("Other Features", rem, "#aaaaaa"))

        self._shap_card._donut.set_segments(segs)
