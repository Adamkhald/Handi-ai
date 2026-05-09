import requests
import config
import logging
from typing import Optional, Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

def _get(endpoint: str, default: Any = None) -> Any:
    """Helper method to execute GET requests with error handling."""
    headers = {}
    if config.API_KEY:
        headers["Authorization"] = f"Bearer {config.API_KEY}"
        
    try:
        response = requests.get(endpoint, headers=headers, timeout=3.0)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.debug(f"API fetch failed for {endpoint}: {e}")
        return default

def fetch_metrics() -> Optional[Dict]:
    """Fetch global dashboard metrics."""
    return _get(config.ENDPOINT_METRICS)

def fetch_chart() -> Optional[Dict]:
    """Fetch production monitoring chart arrays."""
    return _get(config.ENDPOINT_CHART)

def fetch_system() -> Optional[Dict]:
    """Fetch system hardware metrics."""
    return _get(config.ENDPOINT_SYSTEM)

def fetch_log_entry() -> Optional[Dict]:
    """Fetch latest log entry for the prediction stream."""
    return _get(config.ENDPOINT_LOGS)

def fetch_shap() -> Optional[list]:
    """Fetch global SHAP feature importance list."""
    return _get(config.ENDPOINT_SHAP)

def fetch_model_drift() -> Optional[Dict]:
    """Fetch per-model drift scores."""
    return _get(config.ENDPOINT_DRIFT)

def fetch_kpi() -> Optional[Dict]:
    """Fetch system-wide KPIs."""
    return _get(config.ENDPOINT_KPI)
