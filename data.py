"""
HandiAI — Data module
All lists are empty by default. Pages show placeholders until
the user uploads a real model + dataset via Upload & Analyze.
"""

# ── Colour palette constants ──────────────────────────────────────────────────
PURPLE  = "#ffffff"
CYAN    = "#cccccc"
YELLOW  = "#888888"
RED     = "#ffffff"
GREEN   = "#aaaaaa"
BLUE    = "#aaaaaa"
ORANGE  = "#888888"

# ── Summary Metrics (shown on Dashboard) ─────────────────────────────────────
SUMMARY_METRICS = [
    {"title": "Models Loaded",       "value": "—", "trend": "Upload a model",   "color": "#aaaaaa", "icon": "M"},
    {"title": "Prediction Accuracy", "value": "—", "trend": "No data yet",      "color": "#aaaaaa", "icon": "A"},
    {"title": "Production Requests", "value": "—", "trend": "No data yet",      "color": "#aaaaaa", "icon": "R"},
    {"title": "Detected Drift",      "value": "—", "trend": "No data yet",      "color": "#aaaaaa", "icon": "D"},
]

# ── Model registry ────────────────────────────────────────────────────────────
MODELS = []

# ── SHAP features ─────────────────────────────────────────────────────────────
SHAP_FEATURES   = []
SHAP_DONUT_DATA = []

# ── Time series (all empty — charts show blank until real data arrives) ───────
DATES              = []
CONFIDENCE_SERIES  = []
DRIFT_SERIES       = []
TRAFFIC_SPARKLINE  = []
DRIFT_MINI         = []
LATENCY_SERIES     = []

# ── Metrics page defaults ─────────────────────────────────────────────────────
MODEL_METRICS = {
    "accuracy":  0.0,
    "precision": 0.0,
    "recall":    0.0,
    "f1_score":  0.0,
    "roc_auc":   0.0,
}

CONFUSION_MATRIX = [[0]]
CONFUSION_LABELS = ["—"]
ROC_FPR = [0.0, 1.0]
ROC_TPR = [0.0, 1.0]

# ── Production logs ───────────────────────────────────────────────────────────
PRODUCTION_LOGS = []

# ── System metrics (shown as 0 until real data) ───────────────────────────────
SYSTEM_USAGE = {"cpu": 0.0, "gpu": 0.0, "memory": 0.0, "disk_io": 0.0}

# ── Endpoints ─────────────────────────────────────────────────────────────────
ACTIVE_ENDPOINTS = []

# ── Datasets ──────────────────────────────────────────────────────────────────
DATASETS = []

# ── Settings defaults ─────────────────────────────────────────────────────────
SETTINGS = {
    "api_key":            "",
    "base_url":           "http://localhost:8000/api/v1",
    "webhook_url":        "",
    "drift_threshold":    0.15,
    "alert_email":        "",
    "auto_retrain":       False,
    "dark_mode":          True,
    "notification_level": "Critical",
}
