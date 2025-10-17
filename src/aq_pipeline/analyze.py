# src/aq_pipeline/analyze.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import numpy as np
import pandas as pd


@dataclass
class SeriesStats:
    days: int
    coverage_pct: float
    mean: float | None
    max: float | None
    p95: float | None
    trend_slope_per_day: float | None  # µg/m³ per day
    anomalies: int


def _trend_slope_per_day(s: pd.Series) -> float | None:
    """
    Simple OLS slope on daily index (as ordinal) vs value.
    Returns slope in 'units per day'. None if < 3 points.
    """
    s = s.dropna()
    if len(s) < 3:
        return None
    x = s.index.map(pd.Timestamp.toordinal).to_numpy(dtype=float)
    y = s.to_numpy(dtype=float)
    # polyfit degree 1 -> slope
    slope, _intercept = np.polyfit(x, y, 1)
    return float(slope)


def _iqr_anomaly_count(s: pd.Series, k: float = 1.5) -> int:
    """
    Count values outside [Q1 - k*IQR, Q3 + k*IQR].
    Uses non-NA values only.
    """
    s = s.dropna()
    if s.empty:
        return 0
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lo = q1 - k * iqr
    hi = q3 + k * iqr
    return int(((s < lo) | (s > hi)).sum())


def compute_metrics(daily_df: pd.DataFrame) -> Dict[str, SeriesStats]:
    """
    For each pollutant column, compute coverage, moments, p95,
    trend slope (per day), and simple IQR-based anomaly count.
    """
    out: Dict[str, SeriesStats] = {}
    n_days = int(len(daily_df))
    for col in daily_df.columns:
        s = daily_df[col].dropna()
        coverage = 0.0 if n_days == 0 else round(100 * len(s) / n_days, 1)
        mean = float(s.mean()) if not s.empty else None
        vmax = float(s.max()) if not s.empty else None
        p95 = float(s.quantile(0.95)) if not s.empty else None
        slope = _trend_slope_per_day(daily_df[col])
        anomalies = _iqr_anomaly_count(daily_df[col])
        out[col] = SeriesStats(
            days=n_days,
            coverage_pct=coverage,
            mean=mean,
            max=vmax,
            p95=p95,
            trend_slope_per_day=slope,
            anomalies=anomalies,
        )
    return out


def analyze_csv(daily_csv: str | "os.PathLike[str]") -> tuple[pd.DataFrame, Dict[str, SeriesStats]]:
    """
    Convenience: load daily CSV, return (df, metrics).
    """
    df = pd.read_csv(daily_csv, parse_dates=["date"]).set_index("date").sort_index()
    metrics = compute_metrics(df)
    return df, metrics
