"""
HandiAI — Upload & Analyze
Simple two-step form: pick model + CSV, choose target, run.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QProgressBar, QComboBox, QFileDialog, QSizePolicy
)
from PySide6.QtCore import Qt

from widgets.components import Card, add_shadow
from ml_analyzer import MLAnalyzer


# ─────────────────────────────────────────────────────────────
#  File Picker Card
# ─────────────────────────────────────────────────────────────
class _FileCard(Card):
    def __init__(self, title, subtitle, accept_filter, icon, parent=None):
        super().__init__(parent)
        self._filter = accept_filter
        self._path   = ""
        self.on_file = None
        self.setMinimumHeight(130)
        self._build(title, subtitle, icon)

    def _build(self, title, subtitle, icon):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(8)

        top = QHBoxLayout()
        ic  = QLabel(icon)
        ic.setStyleSheet("font-size: 26px; background: transparent;")
        top.addWidget(ic)
        top.addSpacing(8)
        tc = QVBoxLayout(); tc.setSpacing(2)
        t  = QLabel(title)
        t.setStyleSheet("font-size: 13px; font-weight: 700; color: #000000; background: transparent;")
        s  = QLabel(subtitle)
        s.setStyleSheet("font-size: 11px; color: #555555; background: transparent;")
        tc.addWidget(t); tc.addWidget(s)
        top.addLayout(tc); top.addStretch()
        lay.addLayout(top)

        self._status = QLabel("No file selected")
        self._status.setStyleSheet("font-size: 11px; color: #444444; background: transparent;")
        lay.addWidget(self._status)

        btn = QPushButton("Browse…")
        btn.setObjectName("btn_secondary")
        btn.setFixedHeight(30)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._browse)
        lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select file", "", self._filter)
        if path:
            self._path = path
            size_kb = os.path.getsize(path) / 1024
            self._status.setText(f"✓  {os.path.basename(path)}  ({size_kb:.1f} KB)")
            self._status.setStyleSheet(
                "font-size: 11px; color: #555555; background: transparent;"
            )
            if self.on_file:
                self.on_file(path)

    @property
    def path(self):
        return self._path


# ─────────────────────────────────────────────────────────────
#  Upload Page
# ─────────────────────────────────────────────────────────────
class UploadPage(QWidget):
    def __init__(self, engine=None, parent=None):
        super().__init__(parent)
        self.engine    = engine
        self._analyzer = MLAnalyzer(self)
        self.setObjectName("page_container")
        self._build_ui()
        self._wire_analyzer()

    def _build_ui(self):
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
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(24)

        # ── Header ─────────────────────────────────────────────
        t = QLabel("Upload & Analyze")
        t.setStyleSheet(
            "font-size: 24px; font-weight: 800; color: #000000; background: transparent;"
        )
        s = QLabel("Load a scikit-learn model (.pkl / .joblib) and a CSV dataset to compute real metrics.")
        s.setStyleSheet("font-size: 12px; color: #555555; background: transparent;")
        lay.addWidget(t)
        lay.addWidget(s)

        # ── File pickers ───────────────────────────────────────
        file_row = QHBoxLayout()
        file_row.setSpacing(16)

        self._model_card = _FileCard(
            "Model File",
            ".pkl or .joblib  (scikit-learn compatible)",
            "Model files (*.pkl *.joblib *.pickle);;All files (*.*)",
            "⬡",
        )
        add_shadow(self._model_card)
        self._model_card.on_file = self._on_model_file
        file_row.addWidget(self._model_card)

        self._data_card = _FileCard(
            "Dataset CSV",
            "CSV with a header row — must include target column",
            "CSV files (*.csv);;All files (*.*)",
            "⬢",
        )
        add_shadow(self._data_card)
        self._data_card.on_file = self._on_data_file
        file_row.addWidget(self._data_card)

        lay.addLayout(file_row)

        # ── Target column + Run ────────────────────────────────
        run_card = Card()
        add_shadow(run_card)
        rl = QHBoxLayout(run_card)
        rl.setContentsMargins(20, 16, 20, 16)
        rl.setSpacing(16)

        tc_lbl = QLabel("Target column:")
        tc_lbl.setStyleSheet("font-size: 12px; color: #888888; background: transparent;")
        rl.addWidget(tc_lbl)

        self._target_combo = QComboBox()
        self._target_combo.addItem("— load a CSV first —")
        self._target_combo.setEnabled(False)
        self._target_combo.setFixedHeight(34)
        self._target_combo.setMinimumWidth(200)
        rl.addWidget(self._target_combo)

        rl.addStretch()

        self._status_lbl = QLabel("Select a model and dataset to begin.")
        self._status_lbl.setStyleSheet("font-size: 11px; color: #555555; background: transparent;")
        rl.addWidget(self._status_lbl)

        self._run_btn = QPushButton("▶  Run Analysis")
        self._run_btn.setObjectName("btn_primary")
        self._run_btn.setFixedHeight(40)
        self._run_btn.setMinimumWidth(160)
        self._run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._run_btn.clicked.connect(self._run_analysis)
        rl.addWidget(self._run_btn)

        lay.addWidget(run_card)

        # ── Progress bar ───────────────────────────────────────
        self._prog = QProgressBar()
        self._prog.setRange(0, 100)
        self._prog.setValue(0)
        self._prog.setFixedHeight(6)
        self._prog.setTextVisible(False)
        self._prog.hide()
        lay.addWidget(self._prog)

        # ── Results (hidden until done) ────────────────────────
        self._res_card = Card()
        add_shadow(self._res_card)
        self._res_lay = QVBoxLayout(self._res_card)
        self._res_lay.setContentsMargins(20, 16, 20, 16)
        self._res_lay.setSpacing(12)
        self._res_card.hide()
        lay.addWidget(self._res_card)

        lay.addStretch()

    # ── Analyzer signals ───────────────────────────────────────
    def _wire_analyzer(self):
        self._analyzer.progress.connect(self._on_progress)
        self._analyzer.analysis_ready.connect(self._on_done)
        self._analyzer.error.connect(self._on_error)

    def _on_model_file(self, path):
        if self._analyzer.load_model(path):
            self._set_status("Model loaded.", "#aaaaaa")

    def _on_data_file(self, path):
        cols = self._analyzer.load_dataset(path)
        if cols:
            self._target_combo.clear()
            self._target_combo.addItems(cols)
            self._target_combo.setEnabled(True)
            for guess in ["label", "target", "class", "y", "output", cols[-1]]:
                if guess in cols:
                    self._target_combo.setCurrentText(guess)
                    break
            self._set_status(f"Dataset loaded — {len(cols)} columns. Select target.", "#aaaaaa")

    def _run_analysis(self):
        if not self._analyzer._model:
            self._set_status("Please load a model file first.", "#333333"); return
        if self._analyzer._df is None:
            self._set_status("Please load a dataset CSV first.", "#333333"); return
        target = self._target_combo.currentText()
        if not target or target.startswith("—"):
            self._set_status("Please select a target column.", "#333333"); return

        self._run_btn.setEnabled(False)
        self._res_card.hide()
        self._prog.show()
        self._prog.setValue(0)
        self._set_status("Analyzing…", "#888888")
        self._analyzer.run_analysis(target)

    def _on_progress(self, pct, msg):
        self._prog.setValue(pct)
        self._set_status(msg, "#888888")

    def _on_done(self, results):
        self._run_btn.setEnabled(True)
        self._prog.setValue(100)
        self._set_status("Analysis complete.", "#aaaaaa")
        if self.engine:
            self.engine.load_real_data(results)
        self._show_results(results)

    def _on_error(self, msg):
        self._run_btn.setEnabled(True)
        self._prog.hide()
        self._set_status(f"Error: {msg}", "#333333")

    def _set_status(self, msg, color="#555555"):
        self._status_lbl.setText(msg)
        self._status_lbl.setStyleSheet(
            f"font-size: 11px; color: {color}; background: transparent;"
        )

    # ── Results ────────────────────────────────────────────────
    def _show_results(self, r):
        while self._res_lay.count():
            item = self._res_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        m = r["metrics"]

        title = QLabel("Results")
        title.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #000000; background: transparent;"
        )
        self._res_lay.addWidget(title)

        sub = QLabel(
            f"{r['model_type']}  ·  {r['n_samples']:,} samples  ·  "
            f"{r['n_features']} features  ·  {len(r['class_labels'])} classes"
        )
        sub.setStyleSheet("font-size: 11px; color: #555555; background: transparent;")
        self._res_lay.addWidget(sub)

        pills = QHBoxLayout()
        pills.setSpacing(10)
        for name, val in [
            ("Accuracy",  f"{m['accuracy']:.1f}%"),
            ("Precision", f"{m['precision']:.1f}%"),
            ("Recall",    f"{m['recall']:.1f}%"),
            ("F1",        f"{m['f1_score']:.1f}%"),
            ("AUC",       f"{m['roc_auc']:.1f}%"),
        ]:
            w  = QWidget()
            w.setStyleSheet(
                "background: #ebebeb; border: 1px solid #d8d8d8; border-radius: 8px;"
            )
            wl = QVBoxLayout(w)
            wl.setContentsMargins(14, 10, 14, 10)
            wl.setSpacing(2)
            vl = QLabel(val)
            vl.setStyleSheet(
                "font-size: 18px; font-weight: 800; color: #000000; background: transparent;"
            )
            nl = QLabel(name)
            nl.setStyleSheet("font-size: 10px; color: #555555; background: transparent;")
            wl.addWidget(vl)
            wl.addWidget(nl)
            pills.addWidget(w, 1)
        self._res_lay.addLayout(pills)

        note = QLabel(
            "✓  Dashboard, Metrics, Explainability, Drift and Production Logs updated."
        )
        note.setWordWrap(True)
        note.setStyleSheet(
            "font-size: 11px; color: #888888; background: #f0f0f0; "
            "border: 1px solid #d8d8d8; border-radius: 6px; padding: 8px 12px;"
        )
        self._res_lay.addWidget(note)
        self._res_card.show()
