from __future__ import annotations

import logging
from pathlib import Path

# ---------------------------- logging ----------------------------

def get_logger(name: str = "aq_pipeline", level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger; safe to call multiple times without dup handlers."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger

# --------------------------- filesystem --------------------------

def ensure_parent(p: str | Path) -> Path:
    """Ensure parent directory exists and return the path as a Path object."""
    path = Path(p)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

# ------------------------- param mapping -------------------------

# Accept ONLY short names; map to Open-Meteo API names
PARAM_MAP: dict[str, str] = {
    "pm25": "pm2_5",
    "pm10": "pm10",
    "no2":  "nitrogen_dioxide",
    "co":   "carbon_monoxide",
}
ALLOWED_PARAMS = set(PARAM_MAP.keys())

def validate_parameters(params: list[str]) -> list[str]:
    """Ensure params are among: pm25, pm10, no2, co."""
    norm = [p.strip().lower() for p in params]
    bad = [p for p in norm if p not in ALLOWED_PARAMS]
    if bad:
        raise ValueError(f"Unsupported parameters: {bad}. Allowed: {sorted(ALLOWED_PARAMS)}")
    return norm

def to_api_params(params: list[str]) -> list[str]:
    """Map short names to API names, preserving order and removing duplicates."""
    norm = validate_parameters(params)
    seen = set()
    out: list[str] = []
    for p in norm:
        api = PARAM_MAP[p]
        if api not in seen:
            seen.add(api)
            out.append(api)
    return out
