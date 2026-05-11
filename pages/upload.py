"""
HandiAI — Upload & Analyze Page
Drop in your own scikit-learn model (.pkl/.joblib) and test CSV to
compute real metrics, SHAP values, feature drift, and prediction logs.
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
        self._filter   = accept_filter
        self._path     = ""
        self.on_file   = None          # set by UploadPage
        self.setMinimumHeight(150)
        self._build(title, subtitle, icon)

    def _build(self, title, subtitle, icon):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(10)

        top = QHBoxLayout()
        ic  = QLabel(icon)
        ic.setStyleSheet("font-size: 30px; background: transparent;")
        top.addWidget(ic)
        top.addSpacing(10)

        tc = QVBoxLayout(); tc.setSpacing(3)
        t  = QLabel(title)
        t.setStyleSheet("font-size: 14px; font-weight: 700; color: #ffffff; background: transparent;")
        s  = QLabel(subtitle)
        s.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        tc.addWidget(t); tc.addWidget(s)
        top.addLayout(tc); top.addStretch()
        lay.addLayout(top)

        self._status = QLabel("No file selected")
        self._status.setStyleSheet("font-size: 11px; color: #5a5888; background: transparent;")
        lay.addWidget(self._status)

        btn = QPushButton("Browse…")
        btn.setObjectName("btn_secondary")
        btn.setFixedHeight(32)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._browse)
        lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select file", "", self._filter)
        if path:
            self._path = path
            size_kb    = os.path.getsize(path) / 1024
            self._status.setText(f"✓  {os.path.basename(path)}  ({size_kb:.1f} KB)")
            self._status.setStyleSheet("font-size: 11px; color: #00c97d; background: transparent;")
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

    # ── Build ──────────────────────────────────────────────────
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
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(20)

        # Header
        t = QLabel("Upload & Analyze")
        t.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; background: transparent;")
        s = QLabel("Load your own model and dataset to replace simulated data with real metrics, SHAP, and drift")
        s.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        lay.addWidget(t); lay.addWidget(s)

        # ── Step 1 — File pickers ──────────────────────────────
        lay.addWidget(self._step_label("STEP 1 — SELECT FILES"))

        file_row = QHBoxLayout(); file_row.setSpacing(16)

        self._model_card = _FileCard(
            "ML Model File",
            "scikit-learn compatible  (.pkl  or  .joblib)",
            "Model files (*.pkl *.joblib *.pickle);;All files (*.*)",
            "⬡",
        )
        add_shadow(self._model_card)
        self._model_card.on_file = self._on_model_file
        file_row.addWidget(self._model_card)

        self._data_card = _FileCard(
            "Test Dataset (CSV)",
            "CSV with a header row — must include target column",
            "CSV files (*.csv);;All files (*.*)",
            "⬢",
        )
        add_shadow(self._data_card)
        self._data_card.on_file = self._on_data_file
        file_row.addWidget(self._data_card)

        lay.addLayout(file_row)

        # ── Step 2 — Config ────────────────────────────────────
        lay.addWidget(self._step_label("STEP 2 — CONFIGURE TARGET COLUMN"))

        cfg_card = Card()
        add_shadow(cfg_card)
        cl = QHBoxLayout(cfg_card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(24)

        tc_col = QVBoxLayout(); tc_col.setSpacing(6)
        tc_lbl = QLabel("Target Column")
        tc_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff; background: transparent;")
        tc_sub = QLabel("The column your model was trained to predict")
        tc_sub.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        tc_col.addWidget(tc_lbl); tc_col.addWidget(tc_sub)

        self._target_combo = QComboBox()
        self._target_combo.addItem("— load a CSV first —")
        self._target_combo.setEnabled(False)
        self._target_combo.setFixedHeight(36)
        self._target_combo.setMinimumWidth(240)
        tc_col.addWidget(self._target_combo)
        cl.addLayout(tc_col)
        cl.addStretch()

        # Info box
        info = QWidget()
        info.setStyleSheet(
            "background: rgba(180,108,255,0.08); border: 1px solid #b46cff33; border-radius: 10px;"
        )
        il = QVBoxLayout(info); il.setContentsMargins(14, 12, 14, 12); il.setSpacing(4)
        ib = QLabel("Supported formats")
        ib.setStyleSheet("font-size: 12px; font-weight: 700; color: #b46cff; background: transparent;")
        il.addWidget(ib)
        for line in [
            "Model: .pkl, .joblib  (scikit-learn API)",
            "Dataset: .csv with header row",
            "Features: all numeric columns except target",
            "Classes: auto-detected from target column",
        ]:
            lbl = QLabel(line)
            lbl.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
            il.addWidget(lbl)
        cl.addWidget(info)
        lay.addWidget(cfg_card)

        # ── Step 3 — Run ───────────────────────────────────────
        lay.addWidget(self._step_label("STEP 3 — RUN ANALYSIS"))

        run_card = Card()
        add_shadow(run_card)
        rl = QVBoxLayout(run_card)
        rl.setContentsMargins(20, 16, 20, 16)
        rl.setSpacing(12)

        btn_row = QHBoxLayout()
        self._run_btn = QPushButton("▶  Run Analysis")
        self._run_btn.setObjectName("btn_primary")
        self._run_btn.setFixedHeight(44)
        self._run_btn.setMinimumWidth(180)
        self._run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._run_btn.clicked.connect(self._run_analysis)
        btn_row.addWidget(self._run_btn)
        btn_row.addSpacing(16)

        self._status_lbl = QLabel("Ready — load a model and dataset to begin.")
        self._status_lbl.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        btn_row.addWidget(self._status_lbl)
        btn_row.addStretch()
        rl.addLayout(btn_row)

        self._prog = QProgressBar()
        self._prog.setRange(0, 100)
        self._prog.setValue(0)
        self._prog.setFixedHeight(8)
        self._prog.setTextVisible(False)
        self._prog.setStyleSheet(
            "QProgressBar { background: #2e2b5f; border-radius: 4px; border: none; }"
            "QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #b46cff, stop:1 #00e0b8); border-radius: 4px; }"
        )
        self._prog.hide()
        rl.addWidget(self._prog)
        lay.addWidget(run_card)

        # Results card (hidden until analysis completes)
        self._res_card = Card()
        add_shadow(self._res_card)
        self._res_lay  = QVBoxLayout(self._res_card)
        self._res_lay.setContentsMargins(20, 16, 20, 16)
        self._res_lay.setSpacing(14)
        self._res_card.hide()
        lay.addWidget(self._res_card)

        lay.addStretch()

    # ── Signals & callbacks ────────────────────────────────────
    def _wire_analyzer(self):
        self._analyzer.progress.connect(self._on_progress)
        self._analyzer.analysis_ready.connect(self._on_done)
        self._analyzer.error.connect(self._on_error)

    def _on_model_file(self, path):
        if self._analyzer.load_model(path):
            self._set_status("Model loaded successfully.", "#00c97d")

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
            self._set_status(
                f"Dataset loaded — {len(cols)} columns detected. Select target column.",
                "#00c97d",
            )

    def _run_analysis(self):
        if not self._analyzer._model:
            self._set_status("Please load a model file first.", "#ff5577"); return
        if self._analyzer._df is None:
            self._set_status("Please load a dataset CSV first.", "#ff5577"); return
        target = self._target_combo.currentText()
        if not target or target.startswith("—"):
            self._set_status("Please select a target column.", "#ff5577"); return

        self._run_btn.setEnabled(False)
        self._res_card.hide()
        self._prog.show()
        self._prog.setValue(0)
        self._set_status("Analyzing…", "#b46cff")
        self._analyzer.run_analysis(target)

    def _on_progress(self, pct, msg):
        self._prog.setValue(pct)
        self._set_status(msg, "#b46cff")

    def _on_done(self, results):
        self._run_btn.setEnabled(True)
        self._prog.setValue(100)
        self._set_status("Analysis complete!", "#00c97d")
        if self.engine:
            self.engine.load_real_data(results)
        self._show_results(results)

    def _on_error(self, msg):
        self._run_btn.setEnabled(True)
        self._prog.hide()
        self._set_status(f"Error: {msg}", "#ff5577")

    def _set_status(self, msg, color="#9896c8"):
        self._status_lbl.setText(msg)
        self._status_lbl.setStyleSheet(
            f"font-size: 11px; color: {color}; background: transparent;"
        )

    # ── Results summary ────────────────────────────────────────
    def _show_results(self, r):
        while self._res_lay.count():
            item = self._res_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        m = r["metrics"]

        title = QLabel("Analysis Results")
        title.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #ffffff; background: transparent;"
        )
        self._res_lay.addWidget(title)

        sub = QLabel(
            f"{r['model_type']}  ·  {r['n_samples']:,} samples  ·  "
            f"{r['n_features']} features  ·  {len(r['class_labels'])} classes  ·  "
            f"avg latency {r['avg_latency_ms']:.1f} ms/sample"
        )
        sub.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        self._res_lay.addWidget(sub)

        pills = QHBoxLayout(); pills.setSpacing(12)
        for name, val, color in [
            ("Accuracy",  f"{m['accuracy']:.1f}%",  "#00e0b8"),
            ("Precision", f"{m['precision']:.1f}%", "#b46cff"),
            ("Recall",    f"{m['recall']:.1f}%",    "#ffd400"),
            ("F1-Score",  f"{m['f1_score']:.1f}%",  "#00c97d"),
            ("ROC-AUC",   f"{m['roc_auc']:.1f}%",   "#4d9fff"),
        ]:
            w  = QWidget()
            w.setStyleSheet(
                f"background: {color}16; border: 1px solid {color}44; border-radius: 10px;"
            )
            wl = QVBoxLayout(w); wl.setContentsMargins(14, 10, 14, 10); wl.setSpacing(2)
            vl = QLabel(val)
            vl.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {color}; background: transparent;")
            nl = QLabel(name)
            nl.setStyleSheet("font-size: 10px; color: #9896c8; background: transparent;")
            wl.addWidget(vl); wl.addWidget(nl)
            pills.addWidget(w, 1)
        self._res_lay.addLayout(pills)

        classes_lbl = QLabel(f"Classes detected: {', '.join(r['class_labels'])}")
        classes_lbl.setStyleSheet("font-size: 11px; color: #9896c8; background: transparent;")
        self._res_lay.addWidget(classes_lbl)

        note = QLabel(
            "✓  Dashboard, Metrics, Explainability, Drift Detection and Production Logs "
            "have all been updated with data from your model and dataset."
        )
        note.setWordWrap(True)
        note.setStyleSheet(
            "font-size: 11px; color: #00c97d; background: rgba(0,201,125,0.08); "
            "border: 1px solid #00c97d33; border-radius: 8px; padding: 8px 12px;"
        )
        self._res_lay.addWidget(note)
        self._res_card.show()

    # ── Helpers ────────────────────────────────────────────────
    @staticmethod
    def _step_label(text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "font-size: 10px; font-weight: 700; color: #5a5888; "
            "letter-spacing: 1.5px; background: transparent;"
        )
        return lbl
