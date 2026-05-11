"""
Generate a test regression model + CSV for HandiAI.
Produces:
  - test_regression_model.pkl
  - test_regression_data.csv
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.datasets import make_regression
import joblib

np.random.seed(42)

# ── Generate synthetic dataset ────────────────────────────────
X, y = make_regression(
    n_samples=1000,
    n_features=7,
    n_informative=5,
    noise=15.0,
    random_state=42,
)

feature_names = [
    "square_footage",
    "num_bedrooms",
    "num_bathrooms",
    "lot_size",
    "year_built",
    "garage_spaces",
    "neighborhood_score",
]

df = pd.DataFrame(X, columns=feature_names)
df["house_price"] = y

# ── Train model ───────────────────────────────────────────────
model = GradientBoostingRegressor(
    n_estimators=150, max_depth=4, learning_rate=0.1, random_state=42
)
model.fit(df[feature_names], df["house_price"])

# ── Save ──────────────────────────────────────────────────────
joblib.dump(model, "test_regression_model.pkl")
df.to_csv("test_regression_data.csv", index=False)

print("✓  test_regression_model.pkl")
print("✓  test_regression_data.csv")
print(f"   {len(df)} rows  |  {len(feature_names)} features  |  target column: house_price")
print(f"   Target range: [{y.min():.1f}, {y.max():.1f}]")
