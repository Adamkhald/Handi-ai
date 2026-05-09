"""
HandiAI — Explainable AI Platform
Data module: Generates realistic dummy ML/AI data for all pages.
"""

import random
import math
from datetime import datetime, timedelta


# ── Colour palette constants (reused across charts) ──────────────────────────
PURPLE  = "#b46cff"
CYAN    = "#00e0b8"
YELLOW  = "#ffd400"
RED     = "#ff5577"
GREEN   = "#00c97d"
BLUE    = "#4d9fff"
ORANGE  = "#ff8c42"


# ── Summary Metrics ───────────────────────────────────────────────────────────
SUMMARY_METRICS = [
    {"title": "Models Loaded",       "value": "12",    "trend": "+2 this week",   "color": PURPLE, "icon": "⬡"},
    {"title": "Prediction Accuracy", "value": "96.4%", "trend": "+0.3% vs last",  "color": CYAN,   "icon": "◎"},
    {"title": "Production Requests", "value": "1.2M",  "trend": "+18K today",     "color": YELLOW, "icon": "⚡"},
    {"title": "Detected Drift",      "value": "Low",   "trend": "Stable 7 days",  "color": GREEN,  "icon": "◈"},
]


# ── Model List ────────────────────────────────────────────────────────────────
MODELS = [
    {"name": "fraud_detector_v3",   "type": "XGBoost",       "accuracy": 96.4, "drift": 0.02, "status": "Production", "requests": 845231},
    {"name": "churn_predictor_v2",  "type": "LightGBM",      "accuracy": 91.2, "drift": 0.08, "status": "Production", "requests": 321089},
    {"name": "credit_score_mlp",    "type": "Neural Net",    "accuracy": 88.7, "drift": 0.15, "status": "Staging",    "requests": 12540},
    {"name": "anomaly_detector",    "type": "Isolation Forest","accuracy": 94.1,"drift": 0.03, "status": "Production", "requests": 654321},
    {"name": "sentiment_bert",      "type": "Transformer",   "accuracy": 92.3, "drift": 0.05, "status": "Production", "requests": 432100},
    {"name": "image_classifier",    "type": "ResNet-50",     "accuracy": 97.8, "drift": 0.01, "status": "Testing",    "requests": 0},
    {"name": "demand_forecast",     "type": "Prophet",       "accuracy": 85.6, "drift": 0.12, "status": "Production", "requests": 98765},
    {"name": "nlp_ner_model",       "type": "BERT-NER",      "accuracy": 89.4, "drift": 0.07, "status": "Staging",    "requests": 5432},
    {"name": "price_optimizer",     "type": "CatBoost",      "accuracy": 90.1, "drift": 0.06, "status": "Production", "requests": 211034},
    {"name": "object_detector",     "type": "YOLOv8",        "accuracy": 95.5, "drift": 0.04, "status": "Testing",    "requests": 0},
    {"name": "text_classifier",     "type": "SVM",           "accuracy": 83.2, "drift": 0.21, "status": "Retired",    "requests": 0},
    {"name": "risk_scorer",         "type": "Random Forest", "accuracy": 88.9, "drift": 0.09, "status": "Production", "requests": 176543},
]


# ── SHAP Feature Importance ───────────────────────────────────────────────────
SHAP_FEATURES = [
    {"name": "transaction_amount",  "shap": 0.342, "direction": "positive"},
    {"name": "merchant_category",   "shap": 0.218, "direction": "negative"},
    {"name": "time_of_day",         "shap": 0.156, "direction": "positive"},
    {"name": "location_mismatch",   "shap": 0.131, "direction": "negative"},
    {"name": "user_history_score",  "shap": 0.098, "direction": "positive"},
    {"name": "device_fingerprint",  "shap": 0.031, "direction": "positive"},
    {"name": "card_present",        "shap": 0.024, "direction": "negative"},
]

SHAP_DONUT_DATA = [
    ("transaction_amount", 34, PURPLE),
    ("merchant_category",  22, CYAN),
    ("time_of_day",        16, YELLOW),
    ("location_mismatch",  13, RED),
    ("Other Features",     15, BLUE),
]


# ── Prediction Monitoring Time Series ─────────────────────────────────────────
def generate_time_series(days=30):
    """Return (dates, confidence_series, drift_series)."""
    base = datetime.now() - timedelta(days=days)
    dates, conf, drift = [], [], []
    c_val = 92.0
    d_val = 5.0
    for i in range(days):
        dates.append((base + timedelta(days=i)).strftime("%d %b"))
        c_val += random.uniform(-1.5, 1.5)
        c_val  = max(85, min(98, c_val))
        d_val += random.uniform(-0.8, 0.8)
        d_val  = max(1, min(20, d_val))
        conf.append(round(c_val, 2))
        drift.append(round(d_val, 2))
    return dates, conf, drift


DATES, CONFIDENCE_SERIES, DRIFT_SERIES = generate_time_series(30)


# ── Traffic Sparkline ─────────────────────────────────────────────────────────
def generate_sparkline(n=24):
    base = 15000
    vals = []
    for _ in range(n):
        base += random.randint(-2000, 4000)
        base  = max(5000, min(50000, base))
        vals.append(base)
    return vals

TRAFFIC_SPARKLINE = generate_sparkline()


# ── Drift Score Mini-Series ───────────────────────────────────────────────────
DRIFT_MINI = [round(random.uniform(0.02, 0.18), 3) for _ in range(15)]


# ── Confusion Matrix (4-class) ────────────────────────────────────────────────
CONFUSION_MATRIX = [
    [842, 12, 8, 3],
    [15, 731, 22, 6],
    [9,  18, 698, 11],
    [4,   7,  14, 812],
]
CONFUSION_LABELS = ["Normal", "Fraud", "Anomaly", "High-Risk"]


# ── ROC Curve data ────────────────────────────────────────────────────────────
def roc_curve_data():
    fpr, tpr = [0.0], [0.0]
    for t in [0.95, 0.85, 0.75, 0.6, 0.45, 0.35, 0.25, 0.15, 0.08, 0.04, 0.01]:
        fpr.append(round(1 - t + random.uniform(-0.02, 0.02), 3))
        tpr.append(round(t + random.uniform(-0.02, 0.02), 3))
    fpr.append(1.0); tpr.append(1.0)
    return sorted(fpr), sorted(tpr)

ROC_FPR, ROC_TPR = roc_curve_data()


# ── Model Metrics ─────────────────────────────────────────────────────────────
MODEL_METRICS = {
    "accuracy":  96.4,
    "precision": 94.8,
    "recall":    93.2,
    "f1_score":  94.0,
    "roc_auc":   98.7,
}


# ── Production Logs ───────────────────────────────────────────────────────────
_input_vals = [
    {"amount": 2450.00, "merchant": "Electronics", "hour": 2,  "location_ok": False},
    {"amount": 89.99,   "merchant": "Grocery",     "hour": 14, "location_ok": True},
    {"amount": 15000.0, "merchant": "Jewelry",     "hour": 3,  "location_ok": False},
    {"amount": 320.50,  "merchant": "Restaurant",  "hour": 20, "location_ok": True},
    {"amount": 4999.0,  "merchant": "Online",      "hour": 23, "location_ok": False},
]

def _make_log_entry(offset_seconds=0):
    t = datetime.now() - timedelta(seconds=offset_seconds)
    inp = random.choice(_input_vals)
    pred = random.choice(["Fraud", "Normal", "Anomaly", "High-Risk"])
    conf = round(random.uniform(78, 99), 1)
    lat  = round(random.uniform(5, 120), 1)
    return {
        "timestamp": t.strftime("%H:%M:%S"),
        "model":     random.choice([m["name"] for m in MODELS[:6]]),
        "input":     inp,
        "predicted": pred,
        "confidence": conf,
        "latency_ms": lat,
        "drift_flag": random.random() < 0.1,
        "top_features": random.sample([f["name"] for f in SHAP_FEATURES], 3),
    }

PRODUCTION_LOGS = [_make_log_entry(i * 45) for i in range(50)]


# ── Latency Time Series ───────────────────────────────────────────────────────
LATENCY_SERIES = [round(random.uniform(8, 95), 1) for _ in range(30)]


# ── System Usage ─────────────────────────────────────────────────────────────
SYSTEM_USAGE = {
    "cpu":    round(random.uniform(35, 65), 1),
    "gpu":    round(random.uniform(55, 85), 1),
    "memory": round(random.uniform(40, 70), 1),
    "disk_io": round(random.uniform(20, 50), 1),
}

ACTIVE_ENDPOINTS = [
    {"endpoint": "/predict/fraud",   "rps": 245, "p99_ms": 42,  "status": "Healthy"},
    {"endpoint": "/predict/churn",   "rps": 112, "p99_ms": 67,  "status": "Healthy"},
    {"endpoint": "/predict/anomaly", "rps": 198, "p99_ms": 38,  "status": "Healthy"},
    {"endpoint": "/explain/shap",    "rps": 34,  "p99_ms": 145, "status": "Degraded"},
    {"endpoint": "/predict/credit",  "rps": 89,  "p99_ms": 55,  "status": "Healthy"},
]


# ── Datasets ──────────────────────────────────────────────────────────────────
DATASETS = [
    {"name": "fraud_train_2024",   "rows": 2_400_000, "cols": 42, "type": "Tabular", "size": "1.8 GB"},
    {"name": "churn_validation",   "rows": 150_000,   "cols": 28, "type": "Tabular", "size": "320 MB"},
    {"name": "credit_test_set",    "rows": 80_000,    "cols": 35, "type": "Tabular", "size": "210 MB"},
    {"name": "nlp_corpus_2024",    "rows": 500_000,   "cols": 3,  "type": "Text",    "size": "2.1 GB"},
    {"name": "image_dataset_v2",   "rows": 120_000,   "cols": 1,  "type": "Image",   "size": "45 GB"},
    {"name": "drift_reference",    "rows": 200_000,   "cols": 42, "type": "Tabular", "size": "950 MB"},
]


# ── Settings defaults ─────────────────────────────────────────────────────────
SETTINGS = {
    "api_key":          "handi-sk-***********************f4e9",
    "base_url":         "https://api.handiai.io/v2",
    "webhook_url":      "https://hooks.slack.com/services/T00/B00/xxx",
    "drift_threshold":  0.15,
    "alert_email":      "mlops@company.ai",
    "auto_retrain":     True,
    "dark_mode":        True,
    "notification_level": "Critical",
}
