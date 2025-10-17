# src/aq_pipeline/fetch.py
from __future__ import annotations
from pathlib import Path
import pandas as pd
import requests

from .utils import get_logger, ensure_parent, to_api_params

def fetch_openmeteo(
    lat: float,
    lon: float,
    parameters: list[str],
    out_csv: str | Path,
    past_days: int = 30,
    start_date: str | None = None,
    end_date: str | None = None,
) -> Path:
    """
    Fetch hourly air-quality data from Open-Meteo and save as CSV.

    parameters: e.g. ["pm25","pm10","no2","co"]
    Either provide start_date/end_date (YYYY-MM-DD) or past_days.
    """
    log = get_logger()
    hourly_params = to_api_params(parameters)

    base = "https://air-quality-api.open-meteo.com/v1/air-quality"
    query: dict[str, str | int | float] = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(hourly_params),
        # "timezone": "UTC",  # uncomment if you want UTC explicitly
    }

    if start_date and end_date:
        query["start_date"] = str(start_date)
        query["end_date"] = str(end_date)
        range_desc = f"{start_date}..{end_date}"
    else:
        query["past_days"] = int(past_days)
        range_desc = f"past_days={past_days}"

    log.info(f"Fetching {hourly_params} for ({lat},{lon}) [{range_desc}]")
    r = requests.get(base, params=query, timeout=30)
    r.raise_for_status()
    data = r.json()

    # Convert JSON → DataFrame
    time = data["hourly"]["time"]
    df = pd.DataFrame({"time": pd.to_datetime(time)})
    for api_name in hourly_params:
        df[api_name] = data["hourly"].get(api_name, [None] * len(time))

    out = ensure_parent(out_csv)
    df.to_csv(out, index=False)
    log.info(f"Saved raw data → {out}")
    return out
