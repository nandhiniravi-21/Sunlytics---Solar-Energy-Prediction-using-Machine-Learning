# ☀️ Sunlytics — AI-Based Solar Power Generation Prediction System

A professional, full-stack Flask web application that predicts solar power
generation output using a **Random Forest Regressor** trained on real solar
installation data. Built for final year engineering project review, viva,
placement demonstration, and portfolio use.

---

## Features

- 🔐 **User Authentication** — signup, login, logout, hashed passwords, sessions
- ⚡ **AI Prediction Engine** — instant solar output predictions from live inputs
- 📊 **Analytics Dashboard** — total/today/avg/max/min stats + live charts
- 🕘 **Prediction History** — search, sort, filter, and delete past predictions
- 📄 **PDF Reports** — downloadable, professionally formatted report per prediction
- 🌗 **Dark / Light Mode** — theme preference remembered across visits
- 💡 **Smart Recommendations** — condition-based tips (cloud cover, dust, etc.)
- 📈 **Feature Importance** — visual explanation of what drives the model
- 📱 **Fully Responsive** — desktop, tablet, and mobile

## Tech Stack

| Layer      | Technology                                             |
|------------|---------------------------------------------------------|
| Backend    | Python, Flask, SQLite                                    |
| Frontend   | HTML5, CSS3, Bootstrap 5, JavaScript, Chart.js, Font Awesome |
| ML         | Scikit-learn (Random Forest Regressor), Joblib            |
| Reporting  | ReportLab (PDF generation)                                |

## Project Structure

```
sunlytics/
├── app.py                  # Main Flask application (all routes)
├── train_model.py          # Reproduces the notebook's ML workflow, saves model.pkl
├── model.pkl               # Trained model bundle (model + feature order + metrics)
├── database.db             # SQLite database (auto-created on first run)
├── dataset.csv             # Original uploaded dataset (source of truth — untouched)
├── requirements.txt
├── README.md
├── templates/               # Jinja2 HTML templates
│   ├── base.html
│   ├── home.html / about.html / contact.html
│   ├── login.html / signup.html
│   ├── predict.html / dashboard.html / history.html
│   └── 404.html / 500.html
├── static/
│   ├── css/style.css        # Full design system (light + dark themes)
│   ├── js/ (main.js, predict.js, dashboard.js)
│   └── images/
└── utils/
    ├── db.py                # SQLite schema + connection helpers
    ├── ml.py                # Model loading, prediction, recommendations
    └── pdf_report.py        # PDF report generation
```

## Machine Learning Workflow (from the original notebook)

1. Load `dataset.csv` (10,000 records, unmodified).
2. Drop identifier columns: `Record_ID`, `Operator_Name`, `Installation_ID`.
3. Engineer `Hour` from the `Time` column; drop `Time`.
4. Split into `X` (11 features) / `y` (`Solar_Power_Output`), 80/20 train-test split, `random_state=42`.
5. `RandomForestRegressor` tuned via `GridSearchCV` (5-fold CV, scoring=`r2`) over:
   - `n_estimators`: 25–200
   - `criterion`: `squared_error`
   - `max_depth`: 3, 5, 10
6. Evaluate with R², MAE, MSE, RMSE.
7. Persist the best estimator, feature order, and metrics to `model.pkl` via Joblib.

**Feature order (exact, preserved everywhere):**
`Solar_Irradiance, Panel_Temperature, Ambient_Temperature, Cloud_Cover, Humidity, Wind_Speed, Rainfall, Dust_Level, Panel_Efficiency, Inverter_Efficiency, Hour`

## Setup & Run

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

The app starts at **http://localhost:5000**.

- On first run, if `model.pkl` is missing, it is automatically regenerated from
  `train_model.py` using `dataset.csv`.
- The SQLite database (`database.db`) and its tables are created automatically.

## Notes

- The dataset is used exactly as uploaded — no synthetic data, no external
  downloads, no altered columns or target.
- `app.secret_key` should be overridden via the `SUNLYTICS_SECRET_KEY`
  environment variable in any real deployment.
