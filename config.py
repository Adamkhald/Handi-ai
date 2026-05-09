import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("API_KEY", "")

# Endpoints
ENDPOINT_METRICS = f"{API_BASE_URL}/metrics"
ENDPOINT_CHART   = f"{API_BASE_URL}/chart"
ENDPOINT_SYSTEM  = f"{API_BASE_URL}/system"
ENDPOINT_LOGS    = f"{API_BASE_URL}/logs"
ENDPOINT_SHAP    = f"{API_BASE_URL}/shap"
ENDPOINT_DRIFT   = f"{API_BASE_URL}/drift"
ENDPOINT_KPI     = f"{API_BASE_URL}/kpi"
