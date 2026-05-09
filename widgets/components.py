"""
HandiAI — Reusable Card & Widget Components  (dynamic version)
"""

import math
from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, QRect, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QLinearGradient,
    QConicalGradient, QFont, QPainterPath, QRadialGradient
)


# ─────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────
def add_shadow(widget, blur=30, x_off=0, y_off=6, color="#00000066"):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(x_off, y_off)
    shadow.setColor(QColor(color))
    widget.setGraphicsEffect(shadow)


def make_label(text, size=13, weight=QFont.Weight.Normal, color="#e0dff5"):
    lbl = QLabel(text)
    f = lbl.font()
    f.setPointSize(size)
    f.setWeight(weight)
    lbl.setFont(f)
    lbl.setStyleSheet(f"color: {color}; background: transparent;")
    return lbl


# ─────────────────────────────────────────────────────────────
#  Base Card
# ─────────────────────────────────────────────────────────────
class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.Shape.NoFrame)
        add_shadow(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 16, 16)
        painter.setClipPath(path)
        painter.fillPath(path, QBrush(QColor("#2a2855")))
        painter.setPen(QPen(QColor("#3a3670"), 1))
        painter.drawPath(path)
        painter.end()
        super().paintEvent(event)


# ─────────────────────────────────────────────────────────────
#  Animated Number Label
# ─────────────────────────────────────────────────────────────
class AnimatedValueLabel(QLabel):
    """Counts from old → new value smoothly over ~600 ms."""

    def __init__(self, text="", fmt_fn=None, parent=None):
        super().__init__(text, parent)
        self._fmt_fn   = fmt_fn or (lambda v: str(v))
        self._current  = 0.0
        self._target   = 0.0
        self._timer    = QTimer(self)
        self._timer.timeout.connect(self._step)

    def set_value(self, value: float, instant=False):
        self._target = value
        if instant:
            self._current = value
            self.setText(self._fmt_fn(value))
            return
        if not self._timer.isActive():
            self._timer.start(16)

    def _step(self):
        diff = self._target - self._current
        if abs(diff) < 0.005:
            self._current = self._target
            self.setText(self._fmt_fn(self._current))
            self._timer.stop()
        else:
            self._current += diff * 0.12
            self.setText(self._fmt_fn(self._current))


# ─────────────────────────────────────────────────────────────
#  Metric Summary Card  (dynamic)
# ─────────────────────────────────────────────────────────────
class MetricCard(Card):
    def __init__(self, title, value, trend, icon, accent_color,
                 fmt_fn=None, parent=None):
        super().__init__(parent)
        self.accent   = QColor(accent_color)
        self._fmt_fn  = fmt_fn
        self.setMinimumHeight(110)
        self._setup_ui(title, value, trend, icon, accent_color)

    def _setup_ui(self, title, value, trend, icon, accent):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        # Icon box
        icon_box = QWidget()
        icon_box.setFixedSize(52, 52)
        icon_box.setStyleSheet(
            f"background: {accent}22; border-radius: 12px; border: 1px solid {accent}44;"
        )
        icon_lbl = make_label(icon, size=22, color=accent)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il = QVBoxLayout(icon_box)
        il.setContentsMargins(0, 0, 0, 0)
        il.addWidget(icon_lbl)
        layout.addWidget(icon_box)

        # Text
        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        # Animated value
        self._val_lbl = AnimatedValueLabel(
            value, fmt_fn=self._fmt_fn,
        )
        f = self._val_lbl.font()
        f.setPointSize(22); f.setWeight(QFont.Weight.Bold)
        self._val_lbl.setFont(f)
        self._val_lbl.setStyleSheet("color: #ffffff; background: transparent;")

        self._title_lbl = make_label(title, size=11, color="#9896c8")
        self._trend_lbl = make_label(trend, size=10, color=accent)

        text_col.addStretch()
        text_col.addWidget(self._val_lbl)
        text_col.addWidget(self._title_lbl)
        text_col.addWidget(self._trend_lbl)
        text_col.addStretch()
        layout.addLayout(text_col)
        layout.addStretch()

        btn = QPushButton("→")
        btn.setObjectName("btn_icon")
        btn.setFixedSize(32, 32)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignVCenter)

    # ── Public update API ──────────────────────────────────────
    def set_value(self, raw_value, trend_text=None, instant=False):
        """raw_value can be str (non-numeric) or float/int."""
        if isinstance(raw_value, str):
            # Non-numeric — just set text directly
            self._val_lbl.setText(raw_value)
        else:
            if self._fmt_fn:
                self._val_lbl.set_value(raw_value)
            else:
                self._val_lbl.setText(str(raw_value))
        if trend_text is not None:
            self._trend_lbl.setText(trend_text)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, self.accent)
        c2 = QColor(self.accent); c2.setAlpha(0)
        grad.setColorAt(1, c2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawRoundedRect(0, 8, 3, self.height() - 16, 2, 2)
        painter.end()


# ─────────────────────────────────────────────────────────────
#  Circular Gauge  (animated — already was, keep as-is)
# ─────────────────────────────────────────────────────────────
class CircularGauge(QWidget):
    def __init__(self, value=92, label="Confidence Score", parent=None):
        super().__init__(parent)
        self._target = value
        self._value  = 0.0
        self._label  = label
        self.setMinimumSize(200, 200)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(16)

    def set_value(self, v):
        self._target = max(0, min(100, v))

    def _animate(self):
        diff = self._target - self._value
        if abs(diff) > 0.2:
            self._value += diff * 0.07
            self.update()
        else:
            self._value = self._target

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = min(self.width(), self.height())
        margin = 18
        rect = QRect(margin, margin, s - 2*margin, s - 2*margin)

        pen = QPen(QColor("#2e2b5f"), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, -225 * 16, -270 * 16)

        span   = int(-270 * 16 * self._value / 100)
        conic  = QConicalGradient(rect.center(), 135)
        conic.setColorAt(0.0, QColor("#00e0b8"))
        conic.setColorAt(0.5, QColor("#b46cff"))
        conic.setColorAt(1.0, QColor("#00e0b8"))
        arc_pen = QPen(QBrush(conic), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(arc_pen)
        painter.drawArc(rect, -225 * 16, span)

        if self._value > 1:
            angle_deg = -225 + 270 * self._value / 100
            angle_rad = math.radians(angle_deg)
            cx = rect.center().x() + (rect.width()  / 2) * math.cos(angle_rad)
            cy = rect.center().y() - (rect.height() / 2) * math.sin(angle_rad)
            painter.setPen(Qt.PenStyle.NoPen)
            glow = QRadialGradient(cx, cy, 10)
            glow.setColorAt(0, QColor("#b46cffcc"))
            glow.setColorAt(1, QColor("#b46cff00"))
            painter.setBrush(glow)
            painter.drawEllipse(int(cx-10), int(cy-10), 20, 20)

        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{self._value:.1f}%")

        painter.setPen(QColor("#9896c8"))
        painter.setFont(QFont("Segoe UI", 9))
        lbl_rect = QRect(rect.left(), rect.center().y() + 20, rect.width(), 20)
        painter.drawText(lbl_rect, Qt.AlignmentFlag.AlignCenter, self._label)
        painter.end()


# ─────────────────────────────────────────────────────────────
#  Sparkline Widget  (dynamic data update)
# ─────────────────────────────────────────────────────────────
class Sparkline(QWidget):
    def __init__(self, data_points, color="#00e0b8", fill=True, parent=None):
        super().__init__(parent)
        self._data  = list(data_points)
        self._color = QColor(color)
        self._fill  = fill
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_data(self, data_points):
        self._data = list(data_points)
        self.update()

    def paintEvent(self, event):
        if not self._data or len(self._data) < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        mn, mx = min(self._data), max(self._data)
        span = mx - mn if mx != mn else 1

        def px(i):
            return int(i * (w - 4) / (len(self._data) - 1)) + 2
        def py(v):
            return int(h - 6 - (v - mn) / span * (h - 12))

        path = QPainterPath()
        path.moveTo(px(0), py(self._data[0]))
        for i in range(1, len(self._data)):
            x0, y0 = px(i-1), py(self._data[i-1])
            x1, y1 = px(i),   py(self._data[i])
            mc = (x0 + x1) / 2
            path.cubicTo(mc, y0, mc, y1, x1, y1)

        if self._fill:
            fp = QPainterPath(path)
            fp.lineTo(px(len(self._data)-1), h)
            fp.lineTo(px(0), h)
            fp.closeSubpath()
            grad = QLinearGradient(0, 0, 0, h)
            c = QColor(self._color); c.setAlpha(80)
            grad.setColorAt(0, c)
            c2 = QColor(self._color); c2.setAlpha(0)
            grad.setColorAt(1, c2)
            painter.fillPath(fp, QBrush(grad))

        pen = QPen(self._color, 2, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)
        painter.end()


# ─────────────────────────────────────────────────────────────
#  Donut Chart Widget
# ─────────────────────────────────────────────────────────────
class DonutChart(QWidget):
    def __init__(self, segments, parent=None):
        super().__init__(parent)
        self._segments = segments
        self.setMinimumSize(120, 120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_segments(self, segments):
        self._segments = segments
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = min(self.width(), self.height()) - 16
        x = (self.width() - s) // 2
        y = (self.height() - s) // 2
        rect = QRect(x, y, s, s)
        total = sum(v for _, v, _ in self._segments) or 1
        start = 90 * 16
        for label, val, color in self._segments:
            span = int(-360 * 16 * val / total)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(color))
            painter.drawPie(rect, start, span)
            start += span
        hole = QRect(x + s//4, y + s//4, s//2, s//2)
        painter.setBrush(QColor("#2a2855"))
        painter.drawEllipse(hole)
        painter.end()


# ─────────────────────────────────────────────────────────────
#  SHAP Horizontal Bar Widget  (dynamic)
# ─────────────────────────────────────────────────────────────
class SHAPBarChart(QWidget):
    def __init__(self, features, parent=None):
        super().__init__(parent)
        self._features = list(features)
        self.setMinimumHeight(len(features) * 32 + 20)

    def set_features(self, features):
        self._features = list(features)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        row_h = (h - 10) / max(len(self._features), 1)
        max_shap = max(abs(f["shap"]) for f in self._features) or 1
        bar_area_start = 160
        bar_area_w = w - bar_area_start - 60

        f_label = QFont("Segoe UI", 9)
        f_val   = QFont("Segoe UI", 9, QFont.Weight.Bold)

        for i, feat in enumerate(self._features):
            y  = 5 + i * row_h
            cy = y + row_h / 2
            painter.setPen(QColor("#9896c8"))
            painter.setFont(f_label)
            painter.drawText(QRect(0, int(y), bar_area_start - 8, int(row_h)),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             feat["name"])
            bar_w = int(bar_area_w * abs(feat["shap"]) / max_shap)
            color = QColor("#00c97d") if feat["direction"] == "positive" else QColor("#ff5577")
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(QRect(bar_area_start, int(cy - 6), bar_w, 12), 4, 4)
            painter.setPen(color)
            painter.setFont(f_val)
            painter.drawText(QRect(bar_area_start + bar_w + 6, int(y), 50, int(row_h)),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             f"{feat['shap']:+.3f}")
        painter.end()


# ─────────────────────────────────────────────────────────────
#  System Usage Bar  (dynamic)
# ─────────────────────────────────────────────────────────────
class UsageBar(QWidget):
    def __init__(self, label, value, color="#b46cff", parent=None):
        super().__init__(parent)
        self._label  = label
        self._value  = float(value)
        self._target = float(value)
        self._color  = QColor(color)
        self.setFixedHeight(36)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._step)

    def set_value(self, value: float):
        self._target = max(0.0, min(100.0, value))
        if not self._timer.isActive():
            self._timer.start(16)

    def _step(self):
        diff = self._target - self._value
        if abs(diff) < 0.05:
            self._value = self._target
            self._timer.stop()
        else:
            self._value += diff * 0.10
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        painter.setPen(QColor("#9896c8"))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(QRect(0, 0, 90, h),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         self._label)
        track_rect = QRect(95, h//2 - 5, w - 145, 10)
        painter.setBrush(QColor("#2e2b5f"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(track_rect, 5, 5)
        fill_w = int(track_rect.width() * self._value / 100)
        if fill_w > 0:
            grad = QLinearGradient(track_rect.left(), 0, track_rect.right(), 0)
            grad.setColorAt(0, self._color)
            c2 = QColor(self._color); c2.setAlpha(180)
            grad.setColorAt(1, c2)
            painter.setBrush(grad)
            painter.drawRoundedRect(
                QRect(track_rect.left(), track_rect.top(), fill_w, track_rect.height()),
                5, 5
            )
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(QRect(w - 46, 0, 46, h),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                         f"{self._value:.1f}%")
        painter.end()
