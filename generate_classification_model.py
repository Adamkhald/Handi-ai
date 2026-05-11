"""
Generate a test classification model + CSV for HandiAI.
Produces:
  - test_classification_model.pkl
  - test_classification_data.csv
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
import joblib

np.random.seed(42)

# ── Generate synthetic dataset ────────────────────────────────
X, y = make_classification(
    n_samples=1000,
    n_features=8,
    n_informative=5,
    n_redundant=2,
    n_classes=2,
    class_sep=1.2,
    random_state=42,
)

feature_names = [
    "transaction_amount",
    "merchant_category",
    "time_of_day",
    "location_mismatch",
    "user_history_score",
    "device_fingerprint",
    "card_present",
    "velocity_score",
]

df = pd.DataFrame(X, columns=feature_names)
df["label"] = y

# ── Train model ───────────────────────────────────────────────
model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
model.fit(df[feature_names], df["label"])

# ── Save ──────────────────────────────────────────────────────
joblib.dump(model, "test_classification_model.pkl")
df.to_csv("test_classification_data.csv", index=False)

print("✓  test_classification_model.pkl")
print("✓  test_classification_data.csv")
print(f"   {len(df)} rows  |  {len(feature_names)} features  |  target column: label")
print(f"   Class balance: {df['label'].value_counts().to_dict()}")
