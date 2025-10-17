# src/aq_pipeline/utils.py
import logging
from pathlib import Path

# Human-friendly -> Open-Meteo hourly parameter names
PARAM_MAP = {
    "pm25": "pm2_5",
    "pm10": "pm10",
    "no2": "nitrogen_dioxide",
    "co": "carbon_monoxide",
}
ALLOWED_PARAMS = set(PARAM_MAP.keys())

def get_logger(name: str = "aq_pipeline") -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    return logging.getLogger(name)

def ensure_parent(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def validate_parameters(params: list[str]) -> list[str]:
    bad = [p for p in params if p.lower() not in ALLOWED_PARAMS]
    if bad:
        raise ValueError(f"Unsupported parameters: {bad}. Allowed: {sorted(ALLOWED_PARAMS)}")
    return [p.lower() for p in params]

def to_api_params(params: list[str]) -> list[str]:
    """Map user params (pm25,no2,co,pm10) -> Open-Meteo hourly field names."""
    return [PARAM_MAP[p.lower()] for p in validate_parameters(params)]
