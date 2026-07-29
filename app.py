"""
Sunlytics - AI-Based Solar Power Generation Prediction System
================================================================
Main Flask application entry point.

Routes are organised by concern:
  - Public pages: home, about, contact
  - Auth: signup, login, logout
  - Core app: predict, dashboard, history (login required)
  - APIs: chart data, delete prediction, PDF download
"""
import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from utils import db as db_utils
from utils import ml
from utils.pdf_report import build_prediction_pdf

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get("SUNLYTICS_SECRET_KEY", "sunlytics-dev-secret-key-change-in-production")
app.config["MODEL_PATH"] = os.path.join(BASE_DIR, "model.pkl")

FEATURE_ORDER = None  # populated on startup


# ---------------------------------------------------------------------------
# Startup: ensure DB + model are ready
# ---------------------------------------------------------------------------
def ensure_model():
    """Generate model.pkl from the notebook workflow if it doesn't exist."""
    if not os.path.exists(app.config["MODEL_PATH"]):
        import train_model  # executes training script top-to-bottom
    ml.load_model(app.config["MODEL_PATH"])


with app.app_context():
    db_utils.init_db()
    ensure_model()
    FEATURE_ORDER = ml.get_feature_order()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id:
        conn = db_utils.get_db()
        g.user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()


@app.context_processor
def inject_globals():
    return {
        "current_user": g.get("user"),
        "current_year": datetime.now().year,
        "now": datetime.now(),
    }


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    metrics = ml.get_metrics()
    return render_template("home.html", metrics=metrics)


@app.route("/about")
def about():
    metrics = ml.get_metrics()
    feature_importance = ml.get_feature_importance()
    return render_template("about.html", metrics=metrics, feature_importance=feature_importance)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please fill in all required fields.", "danger")
            return render_template("contact.html")

        conn = db_utils.get_db()
        conn.execute(
            "INSERT INTO contact_messages (name, email, subject, message, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, email, subject, message, datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
        conn.close()
        flash("Thank you! Your message has been sent successfully.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters long.")
        if not email or "@" not in email:
            errors.append("Please enter a valid email address.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("signup.html", username=username, email=email)

        conn = db_utils.get_db()
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?", (username, email)
        ).fetchone()
        if existing:
            conn.close()
            flash("Username or email already registered.", "danger")
            return render_template("signup.html", username=username, email=email)

        conn.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, generate_password_hash(password), datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
        conn.close()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = db_utils.get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "danger")
            return render_template("login.html", username=username)

        session.clear()
        session["user_id"] = user["id"]
        flash(f"Welcome back, {user['username']}!", "success")
        next_url = request.args.get("next") or url_for("dashboard")
        return redirect(next_url)

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------
@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    if request.method == "GET":
        return render_template("predict.html", form_data=None)

    # ---- Validate inputs ----
    form = request.form
    errors = []

    def get_float(field, min_v=None, max_v=None, required=True):
        raw = form.get(field, "").strip()
        if raw == "":
            if required:
                errors.append(f"{field.replace('_', ' ')} is required.")
            return None
        try:
            val = float(raw)
        except ValueError:
            errors.append(f"{field.replace('_', ' ')} must be a valid number.")
            return None
        if min_v is not None and val < min_v:
            errors.append(f"{field.replace('_', ' ')} must be at least {min_v}.")
        if max_v is not None and val > max_v:
            errors.append(f"{field.replace('_', ' ')} must be at most {max_v}.")
        return val

    solar_irradiance = get_float("solar_irradiance", 0, 1500)
    panel_temperature = get_float("panel_temperature", -10, 90)
    ambient_temperature = get_float("ambient_temperature", -10, 60)
    cloud_cover = get_float("cloud_cover", 0, 100)
    humidity = get_float("humidity", 0, 100)
    wind_speed = get_float("wind_speed", 0, 100)
    rainfall = get_float("rainfall", 0, 500)
    dust_level = get_float("dust_level", 0, 100)
    panel_efficiency = get_float("panel_efficiency", 0, 100)
    inverter_efficiency = get_float("inverter_efficiency", 0, 100)
    hour = get_float("hour", 0, 23)

    if errors:
        for e in errors:
            flash(e, "danger")
        return render_template("predict.html", form_data=form)

    features = {
        "Solar_Irradiance": solar_irradiance,
        "Panel_Temperature": panel_temperature,
        "Ambient_Temperature": ambient_temperature,
        "Cloud_Cover": cloud_cover,
        "Humidity": humidity,
        "Wind_Speed": wind_speed,
        "Rainfall": rainfall,
        "Dust_Level": dust_level,
        "Panel_Efficiency": panel_efficiency,
        "Inverter_Efficiency": inverter_efficiency,
        "Hour": hour,
    }

    try:
        predicted_output = ml.predict(features)
    except Exception as exc:
        flash(f"Prediction failed: {exc}", "danger")
        return render_template("predict.html", form_data=form)

    status = ml.generation_status(predicted_output)
    recommendation = ml.smart_recommendation(features, predicted_output)

    pred_date = db_utils.now_date()
    pred_time = db_utils.now_time()

    conn = db_utils.get_db()
    cur = conn.execute(
        """
        INSERT INTO predictions (
            user_id, username, prediction_date, prediction_time,
            solar_irradiance, panel_temperature, ambient_temperature, cloud_cover,
            humidity, wind_speed, rainfall, dust_level, panel_efficiency,
            inverter_efficiency, hour, predicted_output, generation_status, recommendation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            g.user["id"], g.user["username"], pred_date, pred_time,
            solar_irradiance, panel_temperature, ambient_temperature, cloud_cover,
            humidity, wind_speed, rainfall, dust_level, panel_efficiency,
            inverter_efficiency, hour, predicted_output, status["label"], " | ".join(recommendation),
        ),
    )
    conn.commit()
    prediction_id = cur.lastrowid
    conn.close()

    result = {
        "id": prediction_id,
        "predicted_output": predicted_output,
        "status": status,
        "recommendation": recommendation,
        "date": pred_date,
        "time": pred_time,
        "features": features,
    }
    return render_template("predict.html", result=result, form_data=None)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    conn = db_utils.get_db()
    user_id = g.user["id"]

    total = conn.execute(
        "SELECT COUNT(*) AS c FROM predictions WHERE user_id = ?", (user_id,)
    ).fetchone()["c"]

    today = db_utils.now_date()
    today_count = conn.execute(
        "SELECT COUNT(*) AS c FROM predictions WHERE user_id = ? AND prediction_date = ?",
        (user_id, today),
    ).fetchone()["c"]

    stats = conn.execute(
        """
        SELECT AVG(predicted_output) AS avg_out,
               MAX(predicted_output) AS max_out,
               MIN(predicted_output) AS min_out
        FROM predictions WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()

    recent = conn.execute(
        "SELECT * FROM predictions WHERE user_id = ? ORDER BY id DESC LIMIT 5",
        (user_id,),
    ).fetchall()
    conn.close()

    cards = {
        "total": total,
        "today": today_count,
        "avg": round(stats["avg_out"], 2) if stats["avg_out"] is not None else 0,
        "max": round(stats["max_out"], 2) if stats["max_out"] is not None else 0,
        "min": round(stats["min_out"], 2) if stats["min_out"] is not None else 0,
    }

    metrics = ml.get_metrics()
    feature_importance = ml.get_feature_importance()
    return render_template(
        "dashboard.html", cards=cards, recent=recent, metrics=metrics,
        feature_importance=feature_importance,
    )


@app.route("/api/chart-data")
@login_required
def chart_data():
    conn = db_utils.get_db()
    user_id = g.user["id"]

    rows = conn.execute(
        "SELECT prediction_date, predicted_output FROM predictions WHERE user_id = ? ORDER BY id ASC",
        (user_id,),
    ).fetchall()
    conn.close()

    # Line chart: last 20 predictions
    last20 = rows[-20:] if len(rows) > 20 else rows
    line_labels = [f"#{i+1}" for i in range(len(last20))]
    line_values = [round(r["predicted_output"], 2) for r in last20]

    # Bar chart: monthly totals
    monthly = {}
    for r in rows:
        month = r["prediction_date"][:7]  # YYYY-MM
        monthly[month] = monthly.get(month, 0) + r["predicted_output"]
    bar_labels = sorted(monthly.keys())
    bar_values = [round(monthly[m], 2) for m in bar_labels]

    # Pie chart: generation status distribution
    conn = db_utils.get_db()
    status_rows = conn.execute(
        "SELECT generation_status, COUNT(*) AS c FROM predictions WHERE user_id = ? GROUP BY generation_status",
        (user_id,),
    ).fetchall()
    conn.close()
    pie_labels = [r["generation_status"] for r in status_rows]
    pie_values = [r["c"] for r in status_rows]

    return jsonify(
        {
            "line": {"labels": line_labels, "values": line_values},
            "bar": {"labels": bar_labels, "values": bar_values},
            "pie": {"labels": pie_labels, "values": pie_values},
        }
    )


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------
@app.route("/history")
@login_required
def history():
    conn = db_utils.get_db()
    user_id = g.user["id"]

    search = request.args.get("q", "").strip()
    sort = request.args.get("sort", "newest")

    query = "SELECT * FROM predictions WHERE user_id = ?"
    params = [user_id]

    if search:
        query += " AND (generation_status LIKE ? OR prediction_date LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    order_map = {
        "newest": "id DESC",
        "oldest": "id ASC",
        "highest": "predicted_output DESC",
        "lowest": "predicted_output ASC",
    }
    query += f" ORDER BY {order_map.get(sort, 'id DESC')}"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("history.html", rows=rows, search=search, sort=sort)


@app.route("/history/delete/<int:pred_id>", methods=["POST"])
@login_required
def delete_prediction(pred_id):
    conn = db_utils.get_db()
    conn.execute(
        "DELETE FROM predictions WHERE id = ? AND user_id = ?", (pred_id, g.user["id"])
    )
    conn.commit()
    conn.close()
    flash("Prediction record deleted.", "success")
    return redirect(url_for("history"))


@app.route("/history/report/<int:pred_id>")
@login_required
def download_report(pred_id):
    conn = db_utils.get_db()
    row = conn.execute(
        "SELECT * FROM predictions WHERE id = ? AND user_id = ?", (pred_id, g.user["id"])
    ).fetchone()
    conn.close()

    if row is None:
        flash("Prediction record not found.", "danger")
        return redirect(url_for("history"))

    features = {
        "Solar_Irradiance": row["solar_irradiance"],
        "Panel_Temperature": row["panel_temperature"],
        "Ambient_Temperature": row["ambient_temperature"],
        "Cloud_Cover": row["cloud_cover"],
        "Humidity": row["humidity"],
        "Wind_Speed": row["wind_speed"],
        "Rainfall": row["rainfall"],
        "Dust_Level": row["dust_level"],
        "Panel_Efficiency": row["panel_efficiency"],
        "Inverter_Efficiency": row["inverter_efficiency"],
        "Hour": row["hour"],
    }
    record = {
        "id": row["id"],
        "username": row["username"],
        "prediction_date": row["prediction_date"],
        "prediction_time": row["prediction_time"],
        "predicted_output": row["predicted_output"],
        "generation_status": row["generation_status"],
        "recommendation": (row["recommendation"] or "").split(" | "),
        "features": features,
    }
    pdf_buffer = build_prediction_pdf(record)
    filename = f"Sunlytics_Report_{row['id']}.pdf"
    return send_file(pdf_buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
