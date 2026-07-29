"""
Machine Learning utility module for Sunlytics.
Loads the trained model (model.pkl) and provides prediction + smart
recommendation logic. The feature order used here is taken directly from
the persisted model bundle to guarantee it matches training exactly.
"""
import joblib
import numpy as np
import pandas as pd

_bundle = None


def load_model(path="model.pkl"):
    global _bundle
    if _bundle is None:
        _bundle = joblib.load(path)
    return _bundle


def get_feature_order():
    bundle = load_model()
    return bundle["feature_order"]


def get_metrics():
    bundle = load_model()
    return bundle.get("metrics", {})


def get_feature_importance():
    """Return a list of {feature, importance} dicts, sorted descending."""
    bundle = load_model()
    model = bundle["model"]
    order = bundle["feature_order"]
    pairs = sorted(
        zip(order, model.feature_importances_.tolist()),
        key=lambda p: p[1], reverse=True
    )
    return [{"feature": f, "importance": round(v, 4)} for f, v in pairs]


def predict(features: dict):
    """
    features: dict keyed by the exact feature names used in training:
      Solar_Irradiance, Panel_Temperature, Ambient_Temperature, Cloud_Cover,
      Humidity, Wind_Speed, Rainfall, Dust_Level, Panel_Efficiency,
      Inverter_Efficiency, Hour
    Returns the predicted Solar_Power_Output (float, kWh).
    """
    bundle = load_model()
    model = bundle["model"]
    order = bundle["feature_order"]

    row = pd.DataFrame([[features[col] for col in order]], columns=order)
    prediction = model.predict(row)[0]
    return max(float(prediction), 0.0)


def generation_status(predicted_output: float) -> dict:
    """Classify predicted output into a status band with a color/badge."""
    if predicted_output >= 3.0:
        return {"label": "High Generation", "level": "success"}
    elif predicted_output >= 1.0:
        return {"label": "Moderate Generation", "level": "warning"}
    else:
        return {"label": "Low Generation", "level": "danger"}


def smart_recommendation(features: dict, predicted_output: float) -> list:
    """
    Produce short, human-readable recommendations based on the input
    conditions, mirroring the rule-based logic requested for the project.
    """
    tips = []

    cloud_cover = features.get("Cloud_Cover", 0)
    dust_level = features.get("Dust_Level", 0)
    humidity = features.get("Humidity", 0)
    rainfall = features.get("Rainfall", 0)
    irradiance = features.get("Solar_Irradiance", 0)
    panel_temp = features.get("Panel_Temperature", 0)
    inverter_eff = features.get("Inverter_Efficiency", 0)
    wind_speed = features.get("Wind_Speed", 0)

    if irradiance >= 700 and cloud_cover < 30:
        tips.append("Sunny conditions detected — high solar generation expected.")
    elif cloud_cover >= 60:
        tips.append("High cloud cover detected — lower solar output expected.")

    if dust_level >= 60:
        tips.append("Dust accumulation is high — cleaning the solar panels may improve efficiency.")

    if panel_temp >= 45:
        tips.append("Panel temperature is elevated — efficiency may drop; consider ventilation or cooling.")

    if rainfall > 0:
        tips.append("Rainfall detected — generation may be temporarily reduced, though panels may self-clean.")

    if humidity >= 80:
        tips.append("High humidity levels detected — monitor for condensation on panel surfaces.")

    if inverter_eff < 90:
        tips.append("Inverter efficiency is below optimal — a maintenance check is recommended.")

    if wind_speed >= 15:
        tips.append("Strong winds detected — verify panel mounting stability.")

    if not tips:
        tips.append("Conditions are within normal operating range for steady solar generation.")

    return tips
