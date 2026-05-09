"""
HandiAI — Settings Page
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QLineEdit, QCheckBox,
    QComboBox, QSlider, QSizePolicy
)
from PySide6.QtCore import Qt

import data
from widgets.components import Card, add_shadow


def _section(title, subtitle=""):
    w = QWidget(); w.setStyleSheet("background: transparent;")
    l = QVBoxLayout(w); l.setContentsMargins(0, 0, 0, 0); l.setSpacing(2)
    t = QLabel(title)
    t.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff; background: transparent;")
    l.addWidget(t)
    if subtitle:
        s = QLabel(subtitle)
        s.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        l.addWidget(s)
    return w


def _row_field(label, widget, description=""):
    container = QWidget(); container.setStyleSheet("background: transparent;")
    lay = QVBoxLayout(container); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(4)
    row = QHBoxLayout(); row.setSpacing(12)
    lbl_col = QVBoxLayout(); lbl_col.setSpacing(1)
    lbl = QLabel(label)
    lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #e0dff5; background: transparent;")
    lbl_col.addWidget(lbl)
    if description:
        desc = QLabel(description)
        desc.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
        lbl_col.addWidget(desc)
    row.addLayout(lbl_col)
    row.addStretch()
    row.addWidget(widget)
    lay.addLayout(row)
    return container


def _styled_input(value="", placeholder=""):
    inp = QLineEdit()
    inp.setText(value)
    inp.setPlaceholderText(placeholder)
    inp.setFixedWidth(280)
    inp.setFixedHeight(34)
    inp.setStyleSheet(
        "QLineEdit { background: #1d1b3a; border: 1px solid #3a3670; border-radius: 8px; "
        "padding: 0 12px; color: #e0dff5; font-size: 12px; }"
        "QLineEdit:focus { border: 1px solid #b46cff; }"
    )
    return inp


class ToggleSwitch(QWidget):
    """Simple toggle (checkbox-based)."""
    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._cb = QCheckBox()
        self._cb.setChecked(checked)
        self._cb.setStyleSheet(
            "QCheckBox::indicator { width: 36px; height: 20px; border-radius: 10px; "
            "background: #3a3670; border: none; }"
            "QCheckBox::indicator:checked { background: #b46cff; }"
        )
        lay.addWidget(self._cb)


class SettingsPage(QWidget):
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
        lay.setSpacing(24)

        # Header
        t = QLabel("Settings")
        t.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; background: transparent;")
        s = QLabel("Configure your HandiAI platform preferences and integrations")
        s.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        lay.addWidget(t); lay.addWidget(s)

        # ── 2-column grid for settings cards ─────────────────
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # ── Card: API Integration ─────────────────────────────
        api_card = Card()
        add_shadow(api_card)
        al = QVBoxLayout(api_card)
        al.setContentsMargins(20, 16, 20, 16)
        al.setSpacing(14)
        al.addWidget(_section("API Integration", "Connect HandiAI to external services"))

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #2e2b5f; max-height: 1px;")
        al.addWidget(sep)

        al.addWidget(_row_field("API Key",
            _styled_input(data.SETTINGS["api_key"]),
            "Your HandiAI API key — keep this secret"))
        al.addWidget(_row_field("Base URL",
            _styled_input(data.SETTINGS["base_url"])))
        al.addWidget(_row_field("Webhook URL",
            _styled_input(data.SETTINGS["webhook_url"]),
            "Slack / Teams webhook for alerts"))

        save_btn = QPushButton("Save API Settings")
        save_btn.setObjectName("btn_primary")
        save_btn.setFixedHeight(34)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        al.addWidget(save_btn)
        grid.addWidget(api_card, 0, 0)

        # ── Card: Notification Preferences ───────────────────
        notif_card = Card()
        add_shadow(notif_card)
        nl = QVBoxLayout(notif_card)
        nl.setContentsMargins(20, 16, 20, 16)
        nl.setSpacing(14)
        nl.addWidget(_section("Notifications", "Control when and how you receive alerts"))

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background: #2e2b5f; max-height: 1px;")
        nl.addWidget(sep2)

        nl.addWidget(_row_field("Alert Email",
            _styled_input(data.SETTINGS["alert_email"]),
            "Email address for critical alerts"))

        notif_combo = QComboBox()
        for lvl in ["Critical", "Warning", "Info", "All"]:
            notif_combo.addItem(lvl)
        notif_combo.setCurrentText(data.SETTINGS["notification_level"])
        notif_combo.setFixedWidth(140)
        notif_combo.setFixedHeight(34)
        nl.addWidget(_row_field("Notification Level", notif_combo))

        for label, checked, desc in [
            ("Drift Alerts",       True,  "Alert when drift exceeds threshold"),
            ("Latency Spikes",     True,  "Alert on P99 latency > 200ms"),
            ("Model Error Bursts", False, "Alert on error rate > 1%"),
            ("Weekly Reports",     True,  "Auto-generate weekly summary reports"),
        ]:
            nl.addWidget(_row_field(label, ToggleSwitch(checked), desc))

        grid.addWidget(notif_card, 0, 1)

        # ── Card: Deployment Config ───────────────────────────
        deploy_card = Card()
        add_shadow(deploy_card)
        dl = QVBoxLayout(deploy_card)
        dl.setContentsMargins(20, 16, 20, 16)
        dl.setSpacing(14)
        dl.addWidget(_section("Deployment Configuration", "Model serving and auto-management"))

        sep3 = QFrame(); sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setStyleSheet("background: #2e2b5f; max-height: 1px;")
        dl.addWidget(sep3)

        # Drift threshold slider
        threshold_row = QWidget(); threshold_row.setStyleSheet("background: transparent;")
        tr_lay = QVBoxLayout(threshold_row); tr_lay.setContentsMargins(0, 0, 0, 0); tr_lay.setSpacing(6)
        top_row = QHBoxLayout()
        tl = QLabel("Drift Threshold")
        tl.setStyleSheet("font-size: 12px; font-weight: 600; color: #e0dff5; background: transparent;")
        top_row.addWidget(tl)
        top_row.addStretch()
        self._thresh_val = QLabel(f"{data.SETTINGS['drift_threshold']:.2f}")
        self._thresh_val.setStyleSheet("font-size: 12px; font-weight: 700; color: #b46cff; background: transparent;")
        top_row.addWidget(self._thresh_val)
        tr_lay.addLayout(top_row)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(1, 50)
        slider.setValue(int(data.SETTINGS["drift_threshold"] * 100))
        slider.valueChanged.connect(lambda v: self._thresh_val.setText(f"{v/100:.2f}"))
        tr_lay.addWidget(slider)
        dl.addWidget(threshold_row)

        for label, checked, desc in [
            ("Auto Retrain",       data.SETTINGS["auto_retrain"], "Retrain on drift detection"),
            ("Shadow Mode",        False,                          "Run new model in shadow before promoting"),
            ("Auto-Rollback",      True,                           "Rollback on accuracy drop > 5%"),
            ("Canary Deployments", False,                          "Route 10% traffic to new model first"),
        ]:
            dl.addWidget(_row_field(label, ToggleSwitch(checked), desc))

        grid.addWidget(deploy_card, 1, 0)

        # ── Card: User Management ─────────────────────────────
        user_card = Card()
        add_shadow(user_card)
        ul = QVBoxLayout(user_card)
        ul.setContentsMargins(20, 16, 20, 16)
        ul.setSpacing(14)
        ul.addWidget(_section("User Management", "Team members and access control"))

        sep4 = QFrame(); sep4.setFrameShape(QFrame.Shape.HLine)
        sep4.setStyleSheet("background: #2e2b5f; max-height: 1px;")
        ul.addWidget(sep4)

        users = [
            ("Adham K.",    "ML Engineer",       "#b46cff", "Admin"),
            ("Sarah M.",    "Data Scientist",    "#00e0b8", "Editor"),
            ("James L.",    "MLOps Engineer",    "#ffd400", "Editor"),
            ("Priya R.",    "Research Lead",     "#4d9fff", "Viewer"),
            ("Tom H.",      "Product Manager",   "#ff8c42", "Viewer"),
        ]
        for name, role, color, access in users:
            row = QHBoxLayout(); row.setSpacing(12)

            # Avatar
            av = QWidget(); av.setFixedSize(32, 32)
            av.setStyleSheet(f"background: {color}44; border-radius: 16px; border: 1px solid {color}66;")
            av_lay = QVBoxLayout(av); av_lay.setContentsMargins(0, 0, 0, 0)
            av_lbl = QLabel(name[0])
            av_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {color}; background: transparent;")
            av_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            av_lay.addWidget(av_lbl)
            row.addWidget(av)

            col_lay = QVBoxLayout(); col_lay.setSpacing(0)
            n_lbl = QLabel(name)
            n_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #ffffff; background: transparent;")
            r_lbl = QLabel(role)
            r_lbl.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
            col_lay.addWidget(n_lbl); col_lay.addWidget(r_lbl)
            row.addLayout(col_lay); row.addStretch()

            ac_badge = QLabel(access)
            ac_color = "#b46cff" if access == "Admin" else ("#00e0b8" if access == "Editor" else "#9896c8")
            ac_badge.setStyleSheet(
                f"background: {ac_color}22; border: 1px solid {ac_color}44; border-radius: 8px; "
                f"color: {ac_color}; font-size: 10px; font-weight: 700; padding: 2px 8px;"
            )
            row.addWidget(ac_badge)

            ul.addLayout(row)

        add_user_btn = QPushButton("+ Invite Team Member")
        add_user_btn.setObjectName("btn_secondary")
        add_user_btn.setFixedHeight(32)
        add_user_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ul.addWidget(add_user_btn)

        grid.addWidget(user_card, 1, 1)

        lay.addLayout(grid)

        # ── Card: Theme ───────────────────────────────────────
        theme_card = Card()
        add_shadow(theme_card)
        thl = QHBoxLayout(theme_card)
        thl.setContentsMargins(20, 16, 20, 16)
        thl.setSpacing(24)

        thc = QVBoxLayout(); thc.setSpacing(2)
        tht = QLabel("Appearance")
        tht.setStyleSheet("font-size: 14px; font-weight: 700; color: #ffffff; background: transparent;")
        ths = QLabel("Choose your dashboard theme and colour scheme")
        ths.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        thc.addWidget(tht); thc.addWidget(ths)
        thl.addLayout(thc)
        thl.addStretch()

        for theme, color, active in [
            ("Dark Purple", "#b46cff", True),
            ("Dark Cyan",   "#00e0b8", False),
            ("Dark Amber",  "#ffd400", False),
        ]:
            btn = QPushButton(theme)
            btn.setFixedHeight(34)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if active:
                btn.setStyleSheet(
                    f"QPushButton {{ background: {color}33; border: 2px solid {color}; "
                    f"border-radius: 10px; color: {color}; font-size: 12px; font-weight: 700; padding: 0 16px; }}"
                )
            else:
                btn.setStyleSheet(
                    f"QPushButton {{ background: rgba(255,255,255,0.05); border: 1px solid #3a3670; "
                    f"border-radius: 10px; color: #9896c8; font-size: 12px; padding: 0 16px; }}"
                    f"QPushButton:hover {{ border: 1px solid {color}66; color: {color}; }}"
                )
            thl.addWidget(btn)

        lay.addWidget(theme_card)
        lay.addSpacing(10)
