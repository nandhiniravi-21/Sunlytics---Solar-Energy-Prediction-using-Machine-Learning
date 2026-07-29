"""
Sunlytics — model training script.

Reproduces the EXACT preprocessing and training workflow from the original
Sunlytics.ipynb notebook, using ONLY the bundled dataset.csv (the same file
the user uploaded — untouched, unmodified, no synthetic data).

Run directly:  python train_model.py
Or imported automatically by app.py if model.pkl is missing.
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# ---- Load (ONLY the uploaded dataset — never replaced or synthesized) ----
data = pd.read_csv(DATA_PATH)

# ---- Preprocessing — identical to the notebook ----
data = data.drop(["Record_ID", "Operator_Name", "Installation_ID"], axis=1)
data["Hour"] = pd.to_datetime(data["Time"], format="mixed").dt.hour
data = data.drop("Time", axis=1)

# ---- Features / target — exact order preserved via X = data.drop(target) ----
X = data.drop("Solar_Power_Output", axis=1)
y = data["Solar_Power_Output"]
FEATURE_ORDER = list(X.columns)

# ---- Train/test split — identical params ----
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---- Random Forest Regressor + GridSearchCV — identical config ----
reg = RandomForestRegressor(random_state=42)
parameters = {
    "n_estimators": [25, 50, 75, 100, 125, 150, 175, 200],
    "criterion": ["squared_error"],
    "max_depth": [3, 5, 10],
}
grid_search = GridSearchCV(
    estimator=reg, param_grid=parameters, cv=5, scoring="r2", n_jobs=-1
)
grid_search.fit(X_train, y_train)
best_rf = grid_search.best_estimator_
y_pred = best_rf.predict(X_test)

metrics = {
    "best_params": grid_search.best_params_,
    "r2_score": round(r2_score(y_test, y_pred), 4),
    "mae": round(mean_absolute_error(y_test, y_pred), 4),
    "mse": round(mean_squared_error(y_test, y_pred), 4),
    "rmse": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4),
    "feature_order": FEATURE_ORDER,
    "training_rows": len(data),
}

# ---- Persist model bundle (model + feature order + metrics together) ----
joblib.dump({"model": best_rf, "feature_order": FEATURE_ORDER, "metrics": metrics}, MODEL_PATH)

if __name__ == "__main__":
    print("Best Parameters:", grid_search.best_params_)
    print("R2 Score :", metrics["r2_score"])
    print("MAE      :", metrics["mae"])
    print("MSE      :", metrics["mse"])
    print("RMSE     :", metrics["rmse"])
    print(f"\nModel saved to {MODEL_PATH}")
