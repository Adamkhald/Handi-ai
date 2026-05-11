"""
HandiAI — Matplotlib Chart Widgets  (polished)
"""

import numpy as np
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch
import matplotlib.patheffects as pe
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from collections import deque
import random

import data

# ── Palette ──────────────────────────────────────────────────────────────────
BG       = "#ffffff"
BG_CARD  = "#f8f8f8"
GRID     = "#eeeeee"
TEXT     = "#999999"
LABEL    = "#333333"

# Accent colours
C_INDIGO = "#5b6ef5"   # confidence / primary line
C_TEAL   = "#14b8a6"   # drift / secondary line
C_AMBER  = "#f59e0b"   # latency / warning
C_ROSE   = "#f43f5e"   # negative SHAP
C_EMERALD= "#10b981"   # positive SHAP / traffic
C_VIOLET = "#8b5cf6"   # PR curve
C_SLATE  = "#64748b"   # neutral bars


def _base_style(ax, fig=None):
    """Apply clean, minimal chart style."""
    if fig:
        fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    # Light horizontal grid only
    ax.yaxis.grid(True, color=GRID, linewidth=0.7, linestyle="-", zorder=0)
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    # Spines — only bottom left, very light
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_edgecolor(GRID)
    ax.spines["bottom"].set_edgecolor(GRID)
    ax.tick_params(colors=TEXT, labelsize=8, length=3, width=0.7)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)


def _sparkline_style(ax, fig=None):
    """Minimal style for small inline charts — no axes at all."""
    if fig:
        fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.grid(False)


def _canvas(fig):
    c = FigureCanvas(fig)
    c.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    return c


def _placeholder(ax, canvas, msg):
    ax.text(0.5, 0.5, msg,
            ha="center", va="center", color=TEXT, fontsize=9,
            transform=ax.transAxes, linespacing=1.6)
    try:
        canvas.draw()
    except Exception:
        pass


def _dot(ax, x, y, color, size=40, zorder=6):
    ax.scatter([x], [y], color=color, s=size, zorder=zorder,
               edgecolors="white", linewidths=1.5)


def _smooth(x, y, pts=300):
    try:
        from scipy.interpolate import make_interp_spline
        if len(x) >= 4:
            xnew = np.linspace(x.min(), x.max(), pts)
            return xnew, make_interp_spline(x, y, k=3)(xnew)
    except Exception:
        pass
    return x.astype(float), y.astype(float)


# ─────────────────────────────────────────────────────────────
#  Production Monitoring Chart  — live rolling window
# ─────────────────────────────────────────────────────────────
class ProductionChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(8, 3.2), dpi=100)
        self._fig.subplots_adjust(left=0.06, right=0.97, top=0.88, bottom=0.12)
        self._ax     = self._fig.add_subplot(111)
        self._canvas = _canvas(self._fig)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._canvas)
        self._dates = list(data.DATES)
        self._conf  = list(data.CONFIDENCE_SERIES)
        self._drift = list(data.DRIFT_SERIES)
        self._draw()

    def update_data(self, dates, conf, drift):
        self._dates = dates
        self._conf  = conf
        self._drift = drift
        self._draw()

    def _draw(self):
        ax = self._ax
        ax.clear()
        _base_style(ax, self._fig)

        if not self._conf:
            _placeholder(ax, self._canvas, "Upload a model to see\nproduction predictions")
            return

        x  = np.arange(len(self._conf))
        c  = np.array(self._conf,  dtype=float)
        d  = np.array(self._drift, dtype=float)

        xc, cs = _smooth(x, c)
        xd, ds = _smooth(x, d + 80)   # offset drift into same range

        # Confidence — indigo
        ax.fill_between(xc, cs, 78, alpha=0.10, color=C_INDIGO, zorder=1)
        ax.plot(xc, cs, color=C_INDIGO, linewidth=2.0, zorder=3,
                label="Confidence %", solid_capstyle="round")
        _dot(ax, xc[-1], cs[-1], C_INDIGO)

        # Drift — teal dashed
        ax.fill_between(xd, ds, 78, alpha=0.07, color=C_TEAL, zorder=1)
        ax.plot(xd, ds, color=C_TEAL, linewidth=1.8, linestyle=(0, (6, 3)),
                zorder=2, label="Drift Score (×10)", solid_capstyle="round")
        _dot(ax, xd[-1], ds[-1], C_TEAL)

        step  = max(1, len(self._dates) // 7)
        ticks = list(range(0, len(self._dates), step))
        ax.set_xticks(ticks)
        ax.set_xticklabels(
            [self._dates[i] for i in ticks],
            rotation=0, fontsize=7.5, color=TEXT
        )
        ax.set_ylim(78, 102)
        ax.set_xlim(xc[0] - 0.3, xc[-1] + 0.3)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f"))

        leg = ax.legend(
            facecolor=BG_CARD, edgecolor=GRID, labelcolor=LABEL,
            fontsize=8.5, framealpha=1, borderpad=0.6,
            loc="upper left", handlelength=1.4,
        )
        leg.get_frame().set_linewidth(0.7)

        try:
            self._canvas.draw()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  Traffic Sparkline Chart  — live
# ─────────────────────────────────────────────────────────────
class TrafficChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(4, 1.1), dpi=100)
        self._fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self._ax     = self._fig.add_subplot(111)
        self._canvas = _canvas(self._fig)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._canvas)
        self._y = list(data.TRAFFIC_SPARKLINE)
        self._draw()

    def update_data(self, y):
        self._y = list(y)
        self._draw()

    def _draw(self):
        ax = self._ax
        ax.clear()
        _sparkline_style(ax, self._fig)
        if not self._y:
            return
        y  = np.array(self._y, dtype=float)
        x  = np.arange(len(y))
        xn, yn = _smooth(x, y)
        baseline = y.min() * 0.92
        ax.fill_between(xn, yn, baseline, alpha=0.18, color=C_EMERALD)
        ax.plot(xn, yn, color=C_EMERALD, linewidth=2.0, solid_capstyle="round")
        _dot(ax, xn[-1], yn[-1], C_EMERALD, size=28)
        try:
            self._canvas.draw()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  Drift Mini Chart  — live
# ─────────────────────────────────────────────────────────────
class DriftMiniChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(4, 0.95), dpi=100)
        self._fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self._ax     = self._fig.add_subplot(111)
        self._canvas = _canvas(self._fig)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._canvas)
        self._y = list(data.DRIFT_MINI)
        self._draw()

    def update_data(self, y):
        self._y = list(y)
        self._draw()

    def _draw(self):
        ax = self._ax
        ax.clear()
        _sparkline_style(ax, self._fig)
        if not self._y:
            return
        y  = np.array(self._y, dtype=float)
        x  = np.arange(len(y))
        xn, yn = _smooth(x, y)
        # Threshold line
        ax.axhline(0.15, color=C_AMBER, linewidth=0.9,
                   linestyle=(0, (4, 3)), alpha=0.8, zorder=1)
        ax.fill_between(xn, yn, 0, alpha=0.15, color=C_TEAL)
        ax.plot(xn, yn, color=C_TEAL, linewidth=2.0, solid_capstyle="round", zorder=3)
        _dot(ax, xn[-1], yn[-1], C_TEAL, size=28)
        ax.set_ylim(0, 0.28)
        try:
            self._canvas.draw()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  SHAP Waterfall Chart
# ─────────────────────────────────────────────────────────────
class SHAPWaterfallChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(7, 3.6), dpi=100)
        self._fig.subplots_adjust(left=0.28, right=0.96, top=0.93, bottom=0.1)
        self._ax     = self._fig.add_subplot(111)
        self._canvas = _canvas(self._fig)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._canvas)
        self._features = list(data.SHAP_FEATURES)
        self._draw()

    def update_features(self, features):
        self._features = list(features)
        self._draw()

    def _draw(self):
        ax = self._ax
        ax.clear()
        _base_style(ax, self._fig)
        ax.xaxis.grid(True, color=GRID, linewidth=0.7)
        ax.yaxis.grid(False)

        if not self._features:
            _placeholder(ax, self._canvas, "Upload a model to see\nSHAP waterfall")
            return

        labels = [f["name"] for f in self._features]
        vals   = [f["shap"] if f["direction"] == "positive" else -f["shap"]
                  for f in self._features]
        colors = [C_EMERALD if v >= 0 else C_ROSE for v in vals]
        y_pos  = np.arange(len(labels))

        bars = ax.barh(
            y_pos, vals, color=colors, edgecolor="none",
            height=0.52, zorder=3,
        )
        # Rounded-ish look: add a thin white left border
        for bar in bars:
            bar.set_linewidth(0)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=8.5, color=LABEL)
        ax.set_xlabel("SHAP Value", color=TEXT, fontsize=8)
        ax.axvline(0, color="#cccccc", linewidth=1.0, zorder=2)

        # Value labels
        for bar, val in zip(bars, vals):
            offset = 0.004 if val >= 0 else -0.004
            ax.text(
                val + offset,
                bar.get_y() + bar.get_height() / 2,
                f"{val:+.3f}", va="center",
                ha="left" if val >= 0 else "right",
                color=LABEL, fontsize=7.5, fontweight="600",
            )
        try:
            self._canvas.draw()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  Feature Importance Chart  — live
# ─────────────────────────────────────────────────────────────
class FeatureImportanceChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(6, 3.1), dpi=100)
        self._fig.subplots_adjust(left=0.28, right=0.96, top=0.93, bottom=0.1)
        self._ax     = self._fig.add_subplot(111)
        self._canvas = _canvas(self._fig)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._canvas)
        self._features = list(data.SHAP_FEATURES)
        self._draw()

    def update_features(self, features):
        self._features = list(features)
        self._draw()

    def _draw(self):
        ax = self._ax
        ax.clear()
        _base_style(ax, self._fig)
        ax.xaxis.grid(True, color=GRID, linewidth=0.7)
        ax.yaxis.grid(False)

        if not self._features:
            _placeholder(ax, self._canvas, "Upload a model to see\nfeature importance")
            return

        feats  = sorted(self._features, key=lambda f: f["shap"], reverse=True)
        labels = [f["name"] for f in feats]
        vals   = [f["shap"] for f in feats]
        n      = len(labels)
        y_pos  = np.arange(n)

        # Gradient intensity — brightest bar = most important
        max_v  = max(vals) if vals else 1
        palette= [C_INDIGO, C_TEAL, C_VIOLET, C_AMBER, C_EMERALD,
                  C_ROSE,   C_SLATE]
        colors = [palette[i % len(palette)] for i in range(n)]

        # Alpha gradient: full alpha for first, lighter for rest
        alphas = [max(0.45, 1.0 - i * 0.08) for i in range(n)]

        for i, (yp, v, col, al) in enumerate(zip(y_pos, vals, colors, alphas)):
            ax.barh(yp, v, color=col, alpha=al, edgecolor="none",
                    height=0.50, zorder=3)
            ax.text(v + max_v * 0.015, yp,
                    f"{v:.3f}", va="center", ha="left",
                    color=LABEL, fontsize=7.5, fontweight="600")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=8.5, color=LABEL)
        ax.set_xlabel("Importance", color=TEXT, fontsize=8)
        ax.set_xlim(0, max_v * 1.22)
        try:
            self._canvas.draw()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  Confusion Matrix
# ─────────────────────────────────────────────────────────────
class ConfusionMatrixChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(4, 3.6), dpi=100)
        self._fig.subplots_adjust(left=0.18, right=0.98, top=0.9, bottom=0.18)
        self._ax     = self._fig.add_subplot(111)
        self._canvas = _canvas(self._fig)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._canvas)
        self._cm     = np.array(data.CONFUSION_MATRIX)
        self._labels = list(data.CONFUSION_LABELS)
        self._draw()

    def update_data(self, cm_list, labels):
        self._cm     = np.array(cm_list)
        self._labels = [str(l) for l in labels]
        self._draw()

    def _draw(self):
        ax = self._ax
        ax.clear()
        self._fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.grid(False)

        cm  = self._cm
        lbl = self._labels
        n   = len(lbl)

        import matplotlib as _mpl
        # Custom blue-indigo colormap
        from matplotlib.colors import LinearSegmentedColormap
        cmap = LinearSegmentedColormap.from_list(
            "handi_cm", ["#f0f0ff", "#c7d2fe", C_INDIGO, "#312e81"]
        )
        im = ax.imshow(cm, interpolation="nearest", cmap=cmap, aspect="auto")

        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(n))
        ax.set_xticklabels(lbl, fontsize=8, color=LABEL, rotation=20, ha="right")
        ax.set_yticklabels(lbl, fontsize=8, color=LABEL)
        ax.set_xlabel("Predicted", color=TEXT, fontsize=8)
        ax.set_ylabel("Actual",    color=TEXT, fontsize=8)
        ax.tick_params(length=0)

        thresh = cm.max() / 2.0 if cm.max() > 0 else 1
        for i in range(n):
            for j in range(n):
                ax.text(
                    j, i, str(cm[i, j]),
                    ha="center", va="center", fontsize=9, fontweight="700",
                    color="#ffffff" if cm[i, j] > thresh else LABEL,
                )
        try:
            self._canvas.draw()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  ROC Curve
# ─────────────────────────────────────────────────────────────
class ROCCurveChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(4, 3.6), dpi=100)
        self._fig.subplots_adjust(left=0.14, right=0.97, top=0.9, bottom=0.14)
        self._ax     = self._fig.add_subplot(111)
        self._canvas = _canvas(self._fig)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._canvas)
        self._fpr = []
        self._tpr = []
        self._auc = None
        self._draw()

    def update_data(self, fpr, tpr, auc_pct):
        self._fpr = list(fpr)
        self._tpr = list(tpr)
        self._auc = auc_pct
        self._draw()

    def _draw(self):
        ax = self._ax
        ax.clear()
        _base_style(ax, self._fig)
        ax.xaxis.grid(True, color=GRID, linewidth=0.7)

        if not self._fpr:
            _placeholder(ax, self._canvas, "Upload a model to see\nROC curve")
            return

        fpr = np.array(self._fpr)
        tpr = np.array(self._tpr)

        ax.fill_between(fpr, tpr, alpha=0.12, color=C_INDIGO, zorder=1)
        ax.plot(fpr, tpr, color=C_INDIGO, linewidth=2.2, zorder=3,
                label=f"AUC = {self._auc:.1f}%", solid_capstyle="round")
        _dot(ax, fpr[-1], tpr[-1], C_INDIGO)

        # Diagonal chance line
        ax.plot([0, 1], [0, 1], color=GRID, linewidth=1.2,
                linestyle=(0, (5, 4)), zorder=2)

        ax.set_xlim(-0.01, 1.01)
        ax.set_ylim(-0.01, 1.04)
        ax.set_xlabel("False Positive Rate", color=TEXT, fontsize=8)
        ax.set_ylabel("True Positive Rate",  color=TEXT, fontsize=8)

        leg = ax.legend(facecolor=BG_CARD, edgecolor=GRID, labelcolor=LABEL,
                        fontsize=8.5, framealpha=1)
        leg.get_frame().set_linewidth(0.7)
        try:
            self._canvas.draw()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  Latency Trend Chart  — live rolling
# ─────────────────────────────────────────────────────────────
class LatencyChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(6, 2.4), dpi=100)
        self._fig.subplots_adjust(left=0.08, right=0.98, top=0.9, bottom=0.08)
        self._ax     = self._fig.add_subplot(111)
        self._canvas = _canvas(self._fig)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._canvas)
        self._y = list(data.LATENCY_SERIES)
        self._draw()

    def update_data(self, y):
        self._y = list(y)
        self._draw()

    def _draw(self):
        ax = self._ax
        ax.clear()
        _base_style(ax, self._fig)

        if not self._y:
            return

        y  = np.array(self._y, dtype=float)
        x  = np.arange(len(y))
        xn, yn = _smooth(x, y)

        # P50 threshold reference line
        p50 = float(np.percentile(y, 50))
        ax.axhline(p50, color=C_AMBER, linewidth=0.9,
                   linestyle=(0, (5, 3)), alpha=0.9, zorder=1,
                   label=f"P50 = {p50:.0f} ms")

        ax.fill_between(xn, yn, y.min() * 0.9, alpha=0.12, color=C_AMBER, zorder=2)
        ax.plot(xn, yn, color=C_AMBER, linewidth=2.0,
                zorder=3, solid_capstyle="round")
        _dot(ax, xn[-1], yn[-1], C_AMBER)

        ax.set_xticks([])
        ax.set_ylabel("ms", color=TEXT, fontsize=8)
        ax.set_xlim(xn[0] - 0.3, xn[-1] + 0.3)

        leg = ax.legend(facecolor=BG_CARD, edgecolor=GRID, labelcolor=LABEL,
                        fontsize=8, framealpha=1, loc="upper left")
        leg.get_frame().set_linewidth(0.7)
        try:
            self._canvas.draw()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  Precision-Recall Curve
# ─────────────────────────────────────────────────────────────
class PRCurveChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(4, 3.6), dpi=100)
        self._fig.subplots_adjust(left=0.14, right=0.97, top=0.9, bottom=0.14)
        self._ax     = self._fig.add_subplot(111)
        self._canvas = _canvas(self._fig)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._canvas)
        self._rec  = []
        self._prec = []
        self._ap   = None
        self._draw()

    def update_data(self, recall, precision, ap):
        self._rec  = list(recall)
        self._prec = list(precision)
        self._ap   = ap
        self._draw()

    def _draw(self):
        ax = self._ax
        ax.clear()
        _base_style(ax, self._fig)
        ax.xaxis.grid(True, color=GRID, linewidth=0.7)

        if not self._rec:
            _placeholder(ax, self._canvas, "Upload a model to see\nPrecision-Recall curve")
            return

        rec  = np.array(self._rec)
        prec = np.array(self._prec)

        ax.fill_between(rec, prec, alpha=0.12, color=C_VIOLET, zorder=1)
        ax.plot(rec, prec, color=C_VIOLET, linewidth=2.2, zorder=3,
                label=f"AP = {self._ap:.3f}", solid_capstyle="round")

        ax.set_xlim(-0.01, 1.01)
        ax.set_ylim(-0.01, 1.06)
        ax.set_xlabel("Recall",    color=TEXT, fontsize=8)
        ax.set_ylabel("Precision", color=TEXT, fontsize=8)

        leg = ax.legend(facecolor=BG_CARD, edgecolor=GRID, labelcolor=LABEL,
                        fontsize=8.5, framealpha=1)
        leg.get_frame().set_linewidth(0.7)
        try:
            self._canvas.draw()
        except Exception:
            pass
