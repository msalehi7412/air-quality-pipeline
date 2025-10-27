from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import requests

from .utils import get_logger, ensure_parent, to_api_params

BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
log = get_logger("aq_pipeline")


def fetch_openmeteo(
    *,
    lat: float,
    lon: float,
    parameters: Iterable[str],
    out_csv: str | Path,
    past_days: int | None = 30,
    start_date: str | None = None,
    end_date: str | None = None,
    timeout: int = 30,
) -> Path:
    """
    Fetch hourly air-quality data from Open-Meteo and save as CSV at `out_csv`.
    `parameters` must be short names: pm25, pm10, no2, co.
    """
    hourly_params = to_api_params(list(parameters))

    # Build query parameters
    query: dict[str, str | int | float] = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(hourly_params),
        "timezone": "UTC",
    }

    if start_date and end_date:
        query["start_date"] = start_date
        query["end_date"] = end_date
        range_desc = f"{start_date}..{end_date}"
    else:
        query["past_days"] = int(past_days or 30)
        range_desc = f"past_days={query['past_days']}"

    log.info(f"Fetching {hourly_params} for ({lat},{lon}) [{range_desc}]")

    r = requests.get(BASE_URL, params=query, timeout=timeout)
    r.raise_for_status()
    data = r.json()

    # Normalize JSON → DataFrame (write empty CSV if no data)
    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    if not times:
        df = pd.DataFrame(columns=["time"] + hourly_params)
    else:
        df = pd.DataFrame({"time": pd.to_datetime(times)})
        for api_name in hourly_params:
            df[api_name] = hourly.get(api_name)

    # Ensure directory exists and save CSV
    ensure_parent(out_csv)           # ensure dirs (ignore return)
    out_path = Path(out_csv)         # always build the Path explicitly
    df.to_csv(out_path, index=False)

    log.info(f"Saved raw data → {out_path}")
    return out_path
