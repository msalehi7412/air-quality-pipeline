# src/aq_pipeline/fetch.py
from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Tuple, List

import pandas as pd
import requests

from .utils import get_logger, ensure_parent, to_api_params

BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
log = get_logger("aq_pipeline")

# ---- helpers ---------------------------------------------------------------

def _daterange_chunks(start: date, end: date, chunk_days: int = 90) -> List[Tuple[date, date]]:
    """
    Split [start, end] inclusive into [start_i, end_i] windows of size <= chunk_days.
    Windows are contiguous and cover the full span.
    """
    out: List[Tuple[date, date]] = []
    cur = start
    one = timedelta(days=1)
    while cur <= end:
        chunk_end = min(cur + timedelta(days=chunk_days - 1), end)
        out.append((cur, chunk_end))
        cur = chunk_end + one
    return out


def _fetch_one_window(
    *,
    lat: float,
    lon: float,
    hourly_params: list[str],
    start_date: date | None = None,
    end_date: date | None = None,
    past_days: int | None = None,
    timeout: int = 30,
) -> pd.DataFrame:
    """Fetch a single window (by explicit dates or past_days) and return a tidy DataFrame."""
    params: dict[str, str | int | float] = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(hourly_params),
        "timezone": "UTC",
    }
    if start_date and end_date:
        params["start_date"] = start_date.isoformat()
        params["end_date"] = end_date.isoformat()
        desc = f"{params['start_date']}..{params['end_date']}"
    else:
        params["past_days"] = int(past_days or 30)
        desc = f"past_days={params['past_days']}"

    log.info(f"Fetching {hourly_params} for ({lat},{lon}) [{desc}]")
    r = requests.get(BASE_URL, params=params, timeout=timeout)
    r.raise_for_status()
    js = r.json()
    hourly = js.get("hourly") or {}
    times = hourly.get("time") or []

    if not times:
        # empty frame with correct columns
        return pd.DataFrame(columns=["time"] + hourly_params)

    df = pd.DataFrame({"time": pd.to_datetime(times)})
    for name in hourly_params:
        df[name] = hourly.get(name)
    return df


# ---- public API ------------------------------------------------------------

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

    If the requested span is > ~90 days, this function automatically splits into
    90-day windows and stitches results into one file.
    """
    hourly_params = to_api_params(list(parameters))

    # Resolve date inputs
    sd: date | None = None
    ed: date | None = None
    if start_date and end_date:
        try:
            sd = datetime.strptime(start_date, "%Y-%m-%d").date()
            ed = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError as e:
            raise SystemExit(f"Invalid date format: {e}")
        if sd > ed:
            raise SystemExit(f"start_date {start_date} must be ≤ end_date {end_date}")

    # Decide chunking plan
    frames: List[pd.DataFrame] = []

    if sd and ed:
        span_days = (ed - sd).days + 1
        if span_days <= 92:
            # single window OK
            frames.append(_fetch_one_window(
                lat=lat, lon=lon, hourly_params=hourly_params,
                start_date=sd, end_date=ed, timeout=timeout
            ))
        else:
            # chunk into 90-day windows
            for win_s, win_e in _daterange_chunks(sd, ed, chunk_days=90):
                frames.append(_fetch_one_window(
                    lat=lat, lon=lon, hourly_params=hourly_params,
                    start_date=win_s, end_date=win_e, timeout=timeout
                ))
    else:
        # using past_days (relative to "today")
        days = int(past_days or 30)
        if days <= 92:
            frames.append(_fetch_one_window(
                lat=lat, lon=lon, hourly_params=hourly_params,
                past_days=days, timeout=timeout
            ))
        else:
            # Convert large past_days into explicit date windows
            today = date.today()
            start_full = today - timedelta(days=days - 1)
            for win_s, win_e in _daterange_chunks(start_full, today, chunk_days=90):
                frames.append(_fetch_one_window(
                    lat=lat, lon=lon, hourly_params=hourly_params,
                    start_date=win_s, end_date=win_e, timeout=timeout
                ))

    # Concatenate, de-duplicate, sort, and write
    if frames:
        df_all = pd.concat(frames, ignore_index=True)
    else:
        df_all = pd.DataFrame(columns=["time"] + hourly_params)

    if not df_all.empty:
        df_all = df_all.drop_duplicates(subset=["time"]).sort_values("time")

    # Ensure directory and save
    out_path = ensure_parent(out_csv)
    df_all.to_csv(out_path, index=False)
    log.info(f"Saved raw data → {out_path}")
    return out_path
