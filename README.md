# HandiAI — Explainable AI Operations Platform

HandiAI is a premium, fully-responsive desktop application built with **Python**, **PySide6**, and **Matplotlib**. It serves as a modern, dark-themed MLOps dashboard designed to monitor production machine learning models, detect statistical drift, explain predictions using SHAP values, and track system resources in real-time.

![HandiAI Dashboard Preview](./preview.png)

## 🚀 Features

* **Real-time Monitoring:** Live telemetry charts (latency, req/s, confidence scores) using a non-blocking `QThreadPool` architecture.
* **Explainable AI (XAI):** Built-in visualizers for SHAP waterfall charts, feature importance bars, and donut charts.
* **Drift Detection:** Per-feature and per-model statistical drift tracking with automated status alerts.
* **Production Log Stream:** Filterable prediction audit logs injected dynamically.
* **Performance Metrics:** Confusion matrices, ROC curves, and PR curves.
* **Fluid UI:** Dark futuristic aesthetic featuring neon purple and cyan accents, soft shadows, rounded cards, and smooth animated value transitions.
* **Asynchronous Data Engine:** Capable of seamlessly fetching from REST APIs (like Supabase or FastAPI) with built-in graceful degradation to simulated data if offline.

## 🛠 Tech Stack

* **UI Framework:** [PySide6 (Qt for Python)](https://doc.qt.io/qtforpython-6/)
* **Charting:** [Matplotlib](https://matplotlib.org/) embedded natively via `FigureCanvasQTAgg`
* **Network & Env:** `requests`, `python-dotenv`
* **Data Processing:** `numpy`, `scipy`

## 📦 Project Structure

```text
Handi_ai/
├── main.py                    # Main QMainWindow application entry point
├── engine.py                  # Async DataEngine handling QThreads and Qt Signals
├── api.py                     # REST API client wrapper
├── config.py                  # Environment and endpoint configurations
├── data.py                    # Mock schemas and fallback data
├── requirements.txt           # Python dependencies
├── .env.example               # Template for API keys and URLs
│
├── styles/
│   └── theme.qss              # Global Dark Neon styling engine
│
├── ui/
│   ├── sidebar.py             # Main navigation pane
│   └── topbar.py              # Search bar and status indicators
│
├── charts/
│   └── matplotlib_charts.py   # All native Matplotlib visualizers
│
├── widgets/
│   └── components.py          # Reusable animated UI elements (Cards, Gauges, Sparklines)
│
└── pages/                     # Individual stacked dashboard screens
    ├── dashboard.py           
    ├── monitoring.py
    ├── drift.py
    ├── explainability.py
    ├── metrics.py
    ├── models.py
    ├── datasets.py
    ├── logs.py
    ├── reports.py
    └── settings.py
```

## 💻 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/handi-ai.git
   cd handi-ai
   ```

2. **Install requirements:**
   Make sure you are using Python 3.10 or higher.
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Environment:**
   Copy the example environment file and add your production API URLs if applicable:
   ```bash
   cp .env.example .env
   ```
   *Note: If no API is provided, the platform gracefully falls back to local simulated data so you can still demo the UI.*

4. **Launch the application:**
   ```bash
   python main.py
   ```

## 🔌 Connecting a Real Backend

By default, HandiAI uses a fallback simulation engine so you can see the UI immediately. To connect a live backend (like Supabase, FastAPI, etc.):
1. Update `API_BASE_URL` in your `.env` file.
2. Edit `api.py` to match your specific REST schemas. The `engine.py` background workers will automatically start routing real payloads into the native Qt Signals.
