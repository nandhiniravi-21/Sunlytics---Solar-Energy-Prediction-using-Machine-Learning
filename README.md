# Sunlytics---Solar-Energy-Prediction-using-Machine-Learning

# ☀️ Sunlytics: AI-Powered Solar Power Prediction Web Application

## 📖 Overview

Sunlytics is a full-stack web application that predicts solar power generation using Machine Learning. The project integrates a Flask backend with a React (Vite) frontend, enabling users to input environmental parameters and receive accurate solar power predictions in real time.

The machine learning model is trained on historical solar energy data and deployed through a REST API built with Flask.

---

## ✨ Features

- 🌞 Predict solar power generation
- 🤖 Machine Learning-based prediction
- ⚡ Fast Flask REST API
- 🎨 Modern React (Vite) frontend
- 📊 Prediction history storage
- 📁 CSV dataset support
- 📈 Easy-to-use user interface
- 📱 Responsive design

---

## 🛠️ Tech Stack

### Frontend
- React.js
- Vite
- HTML5
- CSS3
- JavaScript

### Backend
- Flask
- Python

### Machine Learning
- Scikit-learn
- Pandas
- NumPy
- Joblib

### Dataset
- CSV Dataset

---

## 📂 Project Structure

```
Sunlytics
│
├── backend
│   ├── dataset
│   │   └── solar_dataset.csv
│   │
│   ├── models
│   │   └── solar_power_model.pkl
│   │
│   ├── reports
│   │   └── history.json
│   │
│   ├── app.py
│   ├── model_loader.py
│   ├── routes.py
│   ├── utils.py
│   ├── requirements.txt
│   └── venv
│
├── frontend
│   ├── src
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/Sunlytics.git
```

```bash
cd Sunlytics
```

---

## Backend Setup

Navigate to the backend folder.

```bash
cd backend
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate the virtual environment.

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Run the Flask server.

```bash
python app.py
```

The backend will start at

```
http://127.0.0.1:5000
```

---

## Frontend Setup

Open a new terminal.

```bash
cd frontend
```

Install packages.

```bash
npm install
```

Start the React application.

```bash
npm run dev
```

The frontend will run at

```
http://localhost:5173
```

---

## Machine Learning Workflow

1. Data Collection
2. Data Cleaning
3. Feature Engineering
4. Model Training
5. Model Evaluation
6. Model Serialization (.pkl)
7. Flask API Deployment
8. React Frontend Integration

---

## Input Parameters

The model predicts solar power generation based on environmental parameters such as:

- Solar Irradiance
- Temperature
- Humidity
- Wind Speed
- Atmospheric Pressure
- Cloud Cover

---

## Output

The application predicts:

- Estimated Solar Power Generation

---

## Future Improvements

- Live Weather API Integration
- Interactive Dashboard
- User Authentication
- Historical Prediction Analytics
- Cloud Deployment
- Docker Support
- Mobile-Friendly Interface

---

## Author

**Nandhini R**

Bachelor of Engineering – Computer Science

---

## License

This project is licensed under the MIT License.

---

## ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.
