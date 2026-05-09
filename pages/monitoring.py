"""
HandiAI — Production Monitoring Page
"""

import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

import data
from widgets.components import Card, UsageBar, add_shadow
from charts.matplotlib_charts import LatencyChart


class MonitoringPage(QWidget):
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

        # ── Header ────────────────────────────────────────────
        ph = QHBoxLayout()
        col = QVBoxLayout(); col.setSpacing(2)
        t = QLabel("Production Monitoring")
        t.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; background: transparent;")
        s = QLabel("Real-time model performance, drift alerts, and system health")
        s.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        col.addWidget(t); col.addWidget(s)
        ph.addLayout(col); ph.addStretch()

        # Live badge
        live = QLabel("● LIVE")
        live.setStyleSheet(
            "background: rgba(0,201,125,0.12); border: 1px solid #00c97d44; border-radius: 12px; "
            "color: #00c97d; font-size: 12px; font-weight: 700; padding: 4px 14px;"
        )
        ph.addWidget(live)
        lay.addLayout(ph)

        # ── Row 1: System KPI pills ────────────────────────────
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)
        kpis = [
            ("Active Endpoints", "5",      "#00e0b8", "◉"),
            ("Avg Latency",      "34ms",   "#b46cff", "⏱"),
            ("Error Rate",       "0.02%",  "#00c97d", "✓"),
            ("Drift Alerts",     "1",      "#ffd400", "⚑"),
            ("Req/s",            "654",    "#4d9fff", "⚡"),
        ]
        self._kpi_labels = {}
        for title, val, color, icon in kpis:
            card = Card()
            card.setMinimumHeight(88)
            add_shadow(card)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.setSpacing(4)
            top = QHBoxLayout()
            ic = QLabel(icon)
            ic.setStyleSheet(f"font-size: 16px; color: {color}; background: transparent;")
            top.addWidget(ic); top.addStretch()
            cl.addLayout(top)
            vl = QLabel(val)
            vl.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {color}; background: transparent;")
            cl.addWidget(vl)
            self._kpi_labels[title] = vl
            nl = QLabel(title)
            nl.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
            cl.addWidget(nl)
            kpi_row.addWidget(card)
        lay.addLayout(kpi_row)

        # ── Row 2: Latency chart + System Usage ───────────────
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        # Latency
        lat_card = Card()
        add_shadow(lat_card)
        ll = QVBoxLayout(lat_card)
        ll.setContentsMargins(16, 14, 16, 14)
        ll.setSpacing(8)
        lt = QLabel("Response Latency")
        lt.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        ls = QLabel("P50 / P95 / P99 over 30 samples")
        ls.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
        ll.addWidget(lt); ll.addWidget(ls)
        self._latency_chart = LatencyChart()
        ll.addWidget(self._latency_chart)
        row2.addWidget(lat_card, 2)

        # System Usage
        sys_card = Card()
        add_shadow(sys_card)
        sl = QVBoxLayout(sys_card)
        sl.setContentsMargins(18, 16, 18, 16)
        sl.setSpacing(10)
        st = QLabel("System Resources")
        st.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        sl.addWidget(st)

        usages = [
            ("CPU",     data.SYSTEM_USAGE["cpu"],    "#00e0b8"),
            ("GPU",     data.SYSTEM_USAGE["gpu"],    "#b46cff"),
            ("Memory",  data.SYSTEM_USAGE["memory"], "#ffd400"),
            ("Disk I/O",data.SYSTEM_USAGE["disk_io"],"#ff8c42"),
        ]
        self._usage_bars = {}
        for label, val, color in usages:
            bar = UsageBar(label, val, color)
            self._usage_bars[label] = bar
            sl.addWidget(bar)

        sl.addStretch()
        row2.addWidget(sys_card, 1)
        lay.addLayout(row2)

        # ── Row 3: Active Endpoints ───────────────────────────
        ep_card = Card()
        add_shadow(ep_card)
        el = QVBoxLayout(ep_card)
        el.setContentsMargins(20, 16, 20, 16)
        el.setSpacing(10)

        eh = QHBoxLayout()
        et = QLabel("Active Endpoints")
        et.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        eh.addWidget(et); eh.addStretch()
        eb = QPushButton("Manage Endpoints")
        eb.setObjectName("btn_secondary")
        eb.setFixedHeight(28)
        eb.setCursor(Qt.CursorShape.PointingHandCursor)
        eh.addWidget(eb)
        el.addLayout(eh)

        # Table header
        hdr = QHBoxLayout()
        for col_name in ["Endpoint", "Req/s", "P99 ms", "Status", "Actions"]:
            lbl = QLabel(col_name.upper())
            lbl.setStyleSheet(
                "font-size: 10px; font-weight: 700; color: #5a5888; "
                "letter-spacing: 0.8px; background: transparent;"
            )
            hdr.addWidget(lbl, 2 if col_name == "Endpoint" else 1)
        el.addLayout(hdr)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #2e2b5f; max-height: 1px;")
        el.addWidget(sep)

        for ep in data.ACTIVE_ENDPOINTS:
            row = QHBoxLayout()

            nm = QLabel(ep["endpoint"])
            nm.setStyleSheet("font-size: 12px; font-weight: 600; color: #ffffff; background: transparent;")
            row.addWidget(nm, 2)

            rps = QLabel(str(ep["rps"]))
            rps.setStyleSheet("font-size: 11px; color: #00e0b8; font-weight: 600; background: transparent;")
            row.addWidget(rps, 1)

            lat = QLabel(f"{ep['p99_ms']} ms")
            lat_color = "#00c97d" if ep["p99_ms"] < 60 else ("#ffd400" if ep["p99_ms"] < 120 else "#ff5577")
            lat.setStyleSheet(f"font-size: 11px; color: {lat_color}; font-weight: 600; background: transparent;")
            row.addWidget(lat, 1)

            st_color = "#00c97d" if ep["status"] == "Healthy" else "#ffd400"
            st = QLabel(ep["status"])
            st.setStyleSheet(
                f"background: {st_color}22; border: 1px solid {st_color}44; border-radius: 8px; "
                f"color: {st_color}; font-size: 10px; font-weight: 700; padding: 2px 8px;"
            )
            row.addWidget(st, 1)

            for icon in ["⏸", "📊", "🔍"]:
                b = QPushButton(icon)
                b.setFixedSize(28, 28)
                b.setCursor(Qt.CursorShape.PointingHandCursor)
                b.setStyleSheet(
                    "QPushButton { background: rgba(255,255,255,0.05); border: 1px solid #3a3670; "
                    "border-radius: 7px; font-size: 13px; }"
                    "QPushButton:hover { background: rgba(180,108,255,0.2); border: 1px solid #b46cff55; }"
                )
                row.addWidget(b)

            el.addLayout(row)

            if ep != data.ACTIVE_ENDPOINTS[-1]:
                sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
                sep2.setStyleSheet("background: #2a2855; max-height: 1px;")
                el.addWidget(sep2)

        lay.addWidget(ep_card)

        # ── Row 4: WHY THIS PREDICTION + Live Log ─────────────
        row4 = QHBoxLayout()
        row4.setSpacing(16)

        # WHY card
        why_card = Card()
        add_shadow(why_card)
        wl = QVBoxLayout(why_card)
        wl.setContentsMargins(18, 16, 18, 16)
        wl.setSpacing(10)

        wt = QLabel("WHY THIS PREDICTION?")
        wt.setStyleSheet(
            "font-size: 11px; font-weight: 800; color: #b46cff; "
            "letter-spacing: 1.5px; background: transparent;"
        )
        wl.addWidget(wt)

        # Instead of statically populating "WHY THIS PREDICTION", we'll do it dynamically
        self._why_lay = wl
        self._update_why_prediction(data.PRODUCTION_LOGS[0])

        wl.addStretch()
        row4.addWidget(why_card, 1)

        # Live Feed log
        log_card = Card()
        add_shadow(log_card)
        log_lay = QVBoxLayout(log_card)
        log_lay.setContentsMargins(18, 16, 18, 16)
        log_lay.setSpacing(8)

        log_h = QHBoxLayout()
        log_t = QLabel("Live Prediction Feed")
        log_t.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        log_h.addWidget(log_t); log_h.addStretch()
        clr = QPushButton("Clear")
        clr.setObjectName("btn_secondary")
        clr.setFixedHeight(26)
        clr.setCursor(Qt.CursorShape.PointingHandCursor)
        log_h.addWidget(clr)
        log_lay.addLayout(log_h)

        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setStyleSheet(
            "QTextEdit { background: #1a1836; border: 1px solid #3a3670; border-radius: 10px; "
            "color: #c8c7e8; font-size: 11px; font-family: 'Consolas', monospace; padding: 10px; }"
        )
        self._log_view.setMinimumHeight(220)
        log_lay.addWidget(self._log_view)

        clr.clicked.connect(self._log_view.clear)

        # Seed initial logs
        for entry in data.PRODUCTION_LOGS[:10]:
            self._append_log(entry)

        row4.addWidget(log_card, 2)
        lay.addLayout(row4)
        lay.addSpacing(10)

    def _append_log(self, entry):
        pred = entry["predicted"]
        color = "#ff5577" if pred == "Fraud" else ("#ffd400" if pred == "Anomaly" else "#00c97d")
        drift_flag = " ⚑DRIFT" if entry.get("drift_flag") else ""
        line = (
            f'<span style="color:#5a5888">[{entry["timestamp"]}]</span>  '
            f'<span style="color:#9896c8">{entry["model"][:20]}</span>  '
            f'<span style="color:{color};font-weight:bold">{pred}</span>  '
            f'<span style="color:#9896c8">conf={entry["confidence"]:.1f}%  '
            f'lat={entry["latency_ms"]:.0f}ms</span>'
            f'<span style="color:#ffd400">{drift_flag}</span>'
        )
        self._log_view.append(line)
        self._log_view.ensureCursorVisible()

    def _update_why_prediction(self, entry):
        # Clear existing non-title widgets
        while self._why_lay.count() > 1: # keeping the title
            item = self._why_lay.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Delete items inside the layout
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget(): child.widget().deleteLater()
                item.layout().deleteLater()
                
        for key, val in [
            ("Timestamp",  entry["timestamp"]),
            ("Model",      entry["model"]),
            ("Predicted",  entry["predicted"]),
            ("Confidence", f"{entry['confidence']:.1f}%"),
            ("Latency",    f"{entry['latency_ms']:.1f} ms"),
        ]:
            r = QHBoxLayout()
            k = QLabel(key)
            k.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
            val_color = "#ff5577" if key == "Predicted" and entry["predicted"] == "Fraud" else "#ffffff"
            v = QLabel(str(val))
            v.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {val_color}; background: transparent;")
            r.addWidget(k); r.addStretch(); r.addWidget(v)
            self._why_lay.addLayout(r)

        feat_t = QLabel("Top Influential Features")
        feat_t.setStyleSheet("font-size: 11px; font-weight: 700; color: #ffffff; background: transparent;")
        self._why_lay.addWidget(feat_t)

        for i, feat in enumerate(entry["top_features"]):
            colors = ["#00c97d", "#ff5577", "#ffd400"]
            r = QHBoxLayout()
            dot = QLabel(f"{i+1}.")
            dot.setStyleSheet(f"font-size: 11px; color: {colors[i]}; background: transparent;")
            lbl = QLabel(feat)
            lbl.setStyleSheet("font-size: 11px; color: #e0dff5; background: transparent;")
            r.addWidget(dot); r.addWidget(lbl); r.addStretch()
            self._why_lay.addLayout(r)

    def _connect_engine(self):
        self.engine.kpi_updated.connect(self._on_kpi)
        self.engine.latency_updated.connect(self._latency_chart.update_data)
        self.engine.system_updated.connect(self._on_system)
        self.engine.log_entry_added.connect(self._on_log)
        
        # Pre-fill data
        self._on_kpi(self.engine.snapshot_kpi())
        self._latency_chart.update_data(self.engine.snapshot_latency())
        self._on_system(self.engine.snapshot_system())

    def _on_kpi(self, kpi_data):
        if "Active Endpoints" in self._kpi_labels:
            self._kpi_labels["Active Endpoints"].setText(str(kpi_data.get("active_eps", 5)))
            self._kpi_labels["Avg Latency"].setText(f"{kpi_data.get('latency_p99', 34)}ms") # using p99 as avg for simplicity
            self._kpi_labels["Error Rate"].setText(f"{kpi_data.get('err_rate', 0.02):.2f}%")
            self._kpi_labels["Drift Alerts"].setText(str(kpi_data.get("drift_alerts", 0)))
            self._kpi_labels["Req/s"].setText(str(kpi_data.get("rps", 654)))

    def _on_system(self, sys_data):
        if "CPU" in self._usage_bars:
            self._usage_bars["CPU"].set_value(sys_data.get("cpu", 0))
            self._usage_bars["GPU"].set_value(sys_data.get("gpu", 0))
            self._usage_bars["Memory"].set_value(sys_data.get("memory", 0))
            self._usage_bars["Disk I/O"].set_value(sys_data.get("disk_io", 0))

    def _on_log(self, entry):
        self._append_log(entry)
        # Update WHY card with the latest log
        self._update_why_prediction(entry)
