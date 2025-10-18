# src/aq_pipeline/report.py
from __future__ import annotations

from pathlib import Path
import pandas as pd

from .analyze import analyze_csv, SeriesStats
from .utils import get_logger, ensure_parent


def _fmt(x: float | None, nd: int = 2) -> str:
    return "nan" if x is None else f"{x:.{nd}f}"


def write_summary_report(
    daily_csv: str | Path,
    out_txt: str | Path,
    city: str | None = None,
) -> Path:
    """
    Generates a human-readable text report with:
      - date range
      - coverage %
      - mean / max / p95
      - trend slope (µg/m³ per day)
      - anomaly count (IQR rule)
    """
    log = get_logger()
    df, metrics = analyze_csv(daily_csv)

    lines: list[str] = []
    if city:
        lines.append(f"City: {city}")
    if not df.empty:
        lines.append(f"Range: {df.index.min().date()} – {df.index.max().date()}")
    else:
        lines.append("Range: [no data]")

    lines.append("")
    lines.append("Pollutant Summary (daily):")
    lines.append("name | coverage% | mean | max | p95 | trend(µg/m³/day) | anomalies")
    lines.append("-----|-----------|------|-----|-----|-------------------|----------")

    for p, st in metrics.items():
        lines.append(
            f"{p} | "
            f"{_fmt(st.coverage_pct, 1)} | "
            f"{_fmt(st.mean)} | "
            f"{_fmt(st.max)} | "
            f"{_fmt(st.p95)} | "
            f"{_fmt(st.trend_slope_per_day, 3)} | "
            f"{st.anomalies}"
        )

    out_path = ensure_parent(out_txt)
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info(f"Saved report → {out_path}")
    return out_path
