"""
HandiAI — Matplotlib Chart Widgets  (live-refresh version)
"""

import numpy as np
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from collections import deque
import random

import data

BG      = "#ffffff"
BG_CARD = "#f8f8f8"
GRID    = "#e8e8e8"
TEXT    = "#aaaaaa"
WHITE   = "#111111"
PURPLE  = "#555555"
CYAN    = "#333333"
YELLOW  = "#888888"
RED     = "#333333"
GREEN   = "#444444"
BLUE    = "#555555"
ORANGE  = "#777777"


def _style_axes(ax, fig=None):
    if fig:
        fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=TEXT, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.grid(color=GRID, linewidth=0.5, alpha=0.6)


def _canvas(fig):
    c = FigureCanvas(fig)
    c.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    return c


# ─────────────────────────────────────────────────────────────
#  Production Monitoring Chart  — live rolling window
# ─────────────────────────────────────────────────────────────
class ProductionChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(8, 3.5), dpi=100, tight_layout=True)
        self._ax     = self._fig.add_subplot(111)
        self._canvas = _canvas(self._fig)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._canvas)
        # Initial data
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
        _style_axes(ax, self._fig)

        if not self._conf:
            ax.text(0.5, 0.5, "Upload a model to see predictions",
                    ha="center", va="center", color=TEXT, fontsize=9,
                    transform=ax.transAxes)
            try:
                self._canvas.draw()
            except Exception:
                pass
            return

        x = np.arange(len(self._conf))
        c = np.array(self._conf, dtype=float)
        d = np.array(self._drift, dtype=float)

        try:
            from scipy.interpolate import make_interp_spline
            if len(x) >= 4:
                xnew     = np.linspace(x.min(), x.max(), 300)
                c_smooth = make_interp_spline(x, c, k=3)(xnew)
                d_scaled = make_interp_spline(x, d + 80, k=3)(xnew)
            else:
                xnew = x; c_smooth = c; d_scaled = d + 80
        except Exception:
            xnew = x; c_smooth = c; d_scaled = d + 80

        ax.fill_between(xnew, c_smooth, alpha=0.18, color=CYAN)
        ax.plot(xnew, c_smooth, color=CYAN, linewidth=2.2, label="Confidence %")
        ax.fill_between(xnew, d_scaled, alpha=0.12, color=PURPLE)
        ax.plot(xnew, d_scaled, color=PURPLE, linewidth=2.0,
                linestyle="--", label="Drift Score (offset)")

        step  = max(1, len(self._dates) // 7)
        ticks = list(range(0, len(self._dates), step))
        ax.set_xticks(ticks)
        ax.set_xticklabels([self._dates[i] for i in ticks], rotation=0, fontsize=8)
        ax.set_ylim(79, 101)
        ax.set_xlim(xnew[0], xnew[-1])

        ax.legend(facecolor=BG_CARD, edgecolor=GRID, labelcolor=WHITE, fontsize=9)
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
        self._fig    = Figure(figsize=(4, 1.2), dpi=100, tight_layout=True)
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
        _style_axes(ax, self._fig)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_visible(False)
        ax.grid(False)
        y = np.array(self._y, dtype=float)
        x = np.arange(len(y))
        ax.fill_between(x, y, alpha=0.25, color=CYAN)
        ax.plot(x, y, color=CYAN, linewidth=1.8)
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
        self._fig    = Figure(figsize=(4, 1.0), dpi=100, tight_layout=True)
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
        _style_axes(ax, self._fig)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_visible(False)
        ax.grid(False)
        y  = np.array(self._y, dtype=float)
        x  = np.arange(len(y))
        ax.axhline(0.15, color=YELLOW, linewidth=0.8, linestyle="--", alpha=0.7)
        ax.fill_between(x, y, alpha=0.25, color=PURPLE)
        ax.plot(x, y, color=PURPLE, linewidth=1.8)
        ax.set_ylim(0, 0.25)
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
        self._fig    = Figure(figsize=(7, 3.5), dpi=100, tight_layout=True)
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
        _style_axes(ax, self._fig)
        if not self._features:
            ax.text(0.5, 0.5, "Upload a model to see\nSHAP waterfall",
                    ha="center", va="center", color=TEXT, fontsize=9,
                    transform=ax.transAxes)
            try:
                self._canvas.draw()
            except Exception:
                pass
            return
        labels = [f["name"] for f in self._features]
        vals   = [f["shap"] if f["direction"] == "positive" else -f["shap"]
                  for f in self._features]
        colors = [GREEN if v >= 0 else RED for v in vals]
        y_pos  = np.arange(len(labels))
        bars   = ax.barh(y_pos, vals, color=colors, edgecolor="none", height=0.55)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=9, color=WHITE)
        ax.set_xlabel("SHAP Value", color=TEXT, fontsize=9)
        ax.axvline(0, color=GRID, linewidth=1)
        ax.set_facecolor(BG)
        for bar, val in zip(bars, vals):
            ax.text(val + (0.005 if val >= 0 else -0.005),
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:+.3f}", va="center",
                    ha="left" if val >= 0 else "right",
                    color=WHITE, fontsize=8)
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
        self._fig    = Figure(figsize=(6, 3), dpi=100, tight_layout=True)
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
        _style_axes(ax, self._fig)
        if not self._features:
            ax.text(0.5, 0.5, "Upload a model to see\nfeature importance",
                    ha="center", va="center", color=TEXT, fontsize=9,
                    transform=ax.transAxes)
            try:
                self._canvas.draw()
            except Exception:
                pass
            return
        feats  = sorted(self._features, key=lambda f: f["shap"], reverse=True)
        labels = [f["name"] for f in feats]
        vals   = [f["shap"] for f in feats]
        y_pos  = np.arange(len(labels))
        colors = [PURPLE, CYAN, YELLOW, GREEN, BLUE, ORANGE, RED][:len(feats)]
        ax.barh(y_pos, vals, color=colors, edgecolor="none", height=0.55)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=9, color=WHITE)
        ax.set_xlabel("Importance", color=TEXT, fontsize=9)
        ax.set_facecolor(BG)
        try:
            self._canvas.draw()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  Confusion Matrix  (static — recalculated periodically)
# ─────────────────────────────────────────────────────────────
class ConfusionMatrixChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(4, 3.5), dpi=100, tight_layout=True)
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
        _style_axes(ax, self._fig)
        self._fig.patch.set_facecolor(BG)
        cm  = self._cm
        lbl = self._labels
        n   = len(lbl)
        import matplotlib as _mpl
        _cmap = _mpl.colormaps["PuBuGn"] if hasattr(_mpl, "colormaps") else plt.cm.PuBuGn
        ax.imshow(cm, interpolation="nearest", cmap=_cmap)
        ax.set_xticks(np.arange(n)); ax.set_yticks(np.arange(n))
        ax.set_xticklabels(lbl, fontsize=8, color=WHITE, rotation=20, ha="right")
        ax.set_yticklabels(lbl, fontsize=8, color=WHITE)
        thresh = cm.max() / 2 if cm.max() > 0 else 1
        for i in range(n):
            for j in range(n):
                ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                        color=WHITE if cm[i, j] < thresh else "#0d0d0d",
                        fontsize=9, fontweight="bold")
        try:
            self._canvas.draw()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  ROC Curve  (static display, updates on model switch)
# ─────────────────────────────────────────────────────────────
class ROCCurveChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(4, 3.5), dpi=100, tight_layout=True)
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
        _style_axes(ax, self._fig)
        if not self._fpr:
            ax.text(0.5, 0.5, "Upload a model to see\nROC curve",
                    ha="center", va="center", color=TEXT, fontsize=9,
                    transform=ax.transAxes)
            try:
                self._canvas.draw()
            except Exception:
                pass
            return
        ax.plot(self._fpr, self._tpr, color=CYAN, linewidth=2.2,
                label=f"AUC = {self._auc:.1f}%")
        ax.fill_between(self._fpr, self._tpr, alpha=0.15, color=CYAN)
        ax.plot([0, 1], [0, 1], color=GRID, linewidth=1, linestyle="--")
        ax.set_xlim([0, 1]); ax.set_ylim([0, 1.02])
        ax.set_xlabel("FPR", color=TEXT, fontsize=8)
        ax.set_ylabel("TPR", color=TEXT, fontsize=8)
        ax.legend(facecolor=BG_CARD, edgecolor=GRID, labelcolor=WHITE, fontsize=9)
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
        self._fig    = Figure(figsize=(6, 2.5), dpi=100, tight_layout=True)
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
        _style_axes(ax, self._fig)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_visible(False)
        ax.grid(False)
        y = np.array(self._y, dtype=float)
        x = np.arange(len(y))
        ax.axhline(50, color=YELLOW, linewidth=0.8, linestyle="--", alpha=0.7)
        ax.fill_between(x, y, alpha=0.2, color=ORANGE)
        ax.plot(x, y, color=ORANGE, linewidth=2)
        ax.set_ylabel("ms", color=TEXT, fontsize=8)
        try:
            self._canvas.draw()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  Precision-Recall Curve  (static — re-drawn on demand)
# ─────────────────────────────────────────────────────────────
class PRCurveChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fig    = Figure(figsize=(4, 3.5), dpi=100, tight_layout=True)
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
        _style_axes(ax, self._fig)
        if not self._rec:
            ax.text(0.5, 0.5, "Upload a model to see\nPrecision-Recall curve",
                    ha="center", va="center", color=TEXT, fontsize=9,
                    transform=ax.transAxes)
            try:
                self._canvas.draw()
            except Exception:
                pass
            return
        ax.plot(self._rec, self._prec, color=PURPLE, linewidth=2.2,
                label=f"AP = {self._ap:.3f}")
        ax.fill_between(self._rec, self._prec, alpha=0.15, color=PURPLE)
        ax.set_xlim([0, 1]); ax.set_ylim([0, 1.05])
        ax.set_xlabel("Recall",    color=TEXT, fontsize=8)
        ax.set_ylabel("Precision", color=TEXT, fontsize=8)
        ax.legend(facecolor=BG_CARD, edgecolor=GRID, labelcolor=WHITE, fontsize=9)
        try:
            self._canvas.draw()
        except Exception:
            pass
