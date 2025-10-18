# src/dashboard_app.py
from __future__ import annotations

# --- Streamlit must be configured first ---
import streamlit as st
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")

from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import traceback

# ============================ File discovery & loading ============================
def find_processed_files(processed_dir: str | Path = "data/processed") -> Dict[str, Path]:
    """Return {city_slug: latest_processed_csv_path} by picking newest file per city."""
    processed = Path(processed_dir)
    processed.mkdir(parents=True, exist_ok=True)
    files = sorted(processed.glob("*_daily*.csv"))
    latest: Dict[str, Path] = {}
    for p in files:
        # expected: <city>_daily[_YYYY-MM-DD].csv
        stem = p.stem
        city = stem.split("_daily")[0]
        if city not in latest or p.stat().st_mtime > latest[city].stat().st_mtime:
            latest[city] = p
    return latest

def load_daily_df(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=["date"]).set_index("date").sort_index()
    return df

# ============================ Helpers ============================
def kpi_summary(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    out = []
    for c in cols:
        if c in df.columns:
            s = df[c].dropna()
            out.append(
                dict(
                    pollutant=c,
                    mean=np.round(s.mean(), 2) if not s.empty else np.nan,
                    p95=np.round(s.quantile(0.95), 2) if not s.empty else np.nan,
                    max=np.round(s.max(), 2) if not s.empty else np.nan,
                )
            )
    return pd.DataFrame(out)

def get_global_bounds(city_data: dict[str, pd.DataFrame]) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return the min/max date across all selected cities' data."""
    mins, maxs = [], []
    for df in city_data.values():
        if not df.empty:
            mins.append(df.index.min())
            maxs.append(df.index.max())
    if not mins:
        today = pd.Timestamp("today").normalize()
        return today, today
    return min(mins), max(maxs)

# ============================ AQI (US EPA, PM-only) ============================
PM25_BP = [
    (0.0, 12.0, 0, 50),
    (12.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 150.4, 151, 200),
    (150.5, 250.4, 201, 300),
    (250.5, 350.4, 301, 400),
    (350.5, 500.4, 401, 500),
]
PM10_BP = [
    (0, 54, 0, 50),
    (55, 154, 51, 100),
    (155, 254, 101, 150),
    (255, 354, 151, 200),
    (355, 424, 201, 300),
    (425, 504, 301, 400),
    (505, 604, 401, 500),
]

def _to_scalar(x):
    """Coerce pandas/NumPy scalars/Series to a float or np.nan (never a Series)."""
    if x is None:
        return np.nan
    if isinstance(x, (list, tuple)) and len(x) > 0:
        x = x[0]
    if isinstance(x, (pd.Series, pd.Index, np.ndarray)):
        arr = np.asarray(x).ravel()
        return float(arr[0]) if arr.size >= 1 else np.nan
    try:
        return float(x)
    except Exception:
        return np.nan

def _aqi_from_breakpoints(c, bps):
    c = _to_scalar(c)
    if np.isnan(c):
        return None
    for c_low, c_high, i_low, i_high in bps:
        if c_low <= c <= c_high:
            return (i_high - i_low) / (c_high - c_low) * (c - c_low) + i_low
    return None

def pm_aqi_row(pm25, pm10):
    aqi25 = _aqi_from_breakpoints(pm25, PM25_BP)
    aqi10 = _aqi_from_breakpoints(pm10, PM10_BP)
    vals = [v for v in (aqi25, aqi10) if v is not None]
    return max(vals) if vals else None

def add_pm_aqi(df: pd.DataFrame) -> pd.DataFrame:
    """Adds 'AQI_PM' column using PM2.5/PM10 if present."""
    out = df.copy()
    s25 = out["pm2_5"] if "pm2_5" in out.columns else pd.Series(np.nan, index=out.index)
    s10 = out["pm10"]  if "pm10"  in out.columns else pd.Series(np.nan, index=out.index)
    out["AQI_PM"] = [pm_aqi_row(s25.iloc[i], s10.iloc[i]) for i in range(len(out))]
    return out

def aqi_label(aqi: float | None) -> str:
    if aqi is None or (isinstance(aqi, float) and np.isnan(aqi)):
        return "N/A"
    if aqi <= 50:  return "Good"
    if aqi <= 100: return "Moderate"
    if aqi <= 150: return "Unhealthy for Sensitive"
    if aqi <= 200: return "Unhealthy"
    if aqi <= 300: return "Very Unhealthy"
    return "Hazardous"

# ============================ UI ============================
st.title("🌍 Air Quality — Multi-City Dashboard")
st.caption("Data source: Open-Meteo Air Quality API · Daily means from your pipeline")

files = find_processed_files()
if not files:
    st.warning("No processed files found in `data/processed/`.\n\n"
               "Run: `python run_pipeline.py --city milan --past-days 10 --timestamp`")
    st.stop()

# Sidebar controls
city_choices = sorted(files.keys())
sel_cities = st.sidebar.multiselect("Cities", city_choices, default=city_choices[:1])

all_pollutants = ["pm2_5", "pm10", "nitrogen_dioxide", "carbon_monoxide"]
default_pol = [p for p in ["pm2_5", "pm10"] if p in all_pollutants]
sel_pollutants = st.sidebar.multiselect("Pollutants to display", options=all_pollutants, default=default_pol)

# Load data per city + compute global bounds
city_data: Dict[str, pd.DataFrame] = {}
date_min = None
date_max = None
for city in sel_cities:
    try:
        df = load_daily_df(files[city])
        df = add_pm_aqi(df)
        city_data[city] = df
        if not df.empty:
            dmin, dmax = df.index.min(), df.index.max()
            date_min = dmin if date_min is None else min(date_min, dmin)
            date_max = dmax if date_max is None else max(date_max, dmax)
    except Exception as e:
        with st.expander(f"⚠️ Failed to load {city}"):
            st.exception(e)

if date_min is None:
    st.warning("Selected cities have no data.")
    st.stop()

# ---- Responsive date range (bounded + optional auto-clamp)
global_min, global_max = get_global_bounds(city_data)

st.sidebar.markdown("### Date range")
auto_clamp = st.sidebar.checkbox("Auto-clamp to available data", value=True)

start_date, end_date = st.sidebar.date_input(
    "Pick dates within available range",
    (global_min.date(), global_max.date()),
    min_value=global_min.date(),
    max_value=global_max.date(),
)

start_ts = pd.Timestamp(start_date)
end_ts   = pd.Timestamp(end_date)
if auto_clamp:
    start_ts = max(start_ts, global_min)
    end_ts   = min(end_ts,   global_max)

st.sidebar.caption(f"Available data across selected cities: **{global_min.date()} → {global_max.date()}**")

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Time Series", "📊 KPIs", "🧪 AQI (PM-based)"])

# ---- Tab 1: Time Series
with tab1:
    st.subheader("Daily Means")
    for p in sel_pollutants:
        try:
            st.markdown(f"**{p}**")
            df_plot = pd.DataFrame(
                {city: city_data[city].loc[start_ts:end_ts][p]
                 for city in sel_cities if p in city_data[city].columns}
            )
            if df_plot.empty:
                st.info(f"No data for **{p}** in the selected range.")
            else:
                st.line_chart(df_plot)
        except Exception as e:
            with st.expander(f"⚠️ {p} plot failed"):
                st.exception(e)
                st.text(traceback.format_exc())

# ---- Tab 2: KPIs
with tab2:
    try:
        st.subheader("Summary (mean, p95, max)")
        kpi_frames = []
        for city in sel_cities:
            if city not in city_data:
                continue
            df = city_data[city].loc[start_ts:end_ts]
            if df.empty:
                continue
            kpi_frames.append(kpi_summary(df, sel_pollutants).assign(city=city))
        if kpi_frames:
            kpis = pd.concat(kpi_frames, ignore_index=True)
            st.dataframe(kpis, use_container_width=True)
        else:
            st.info("No KPIs to display for the selected filters.")
    except Exception as e:
        with st.expander("⚠️ KPI section failed"):
            st.exception(e)
            st.text(traceback.format_exc())

# ---- Tab 3: AQI (PM-only)
with tab3:
    try:
        st.subheader("Overall AQI (PM₂.₅ / PM₁₀)")
        st.caption("Calculated using US EPA breakpoints (µg/m³). NO₂/CO not included in AQI here.")
        aqi_df = pd.DataFrame(
            {city: city_data[city].loc[start_ts:end_ts]["AQI_PM"]
             for city in sel_cities if "AQI_PM" in city_data[city].columns}
        )
        if aqi_df.empty:
            st.info("No AQI values in the selected range.")
        else:
            st.line_chart(aqi_df)
            st.markdown("**Latest AQI (by city)**")
            latest = []
            for city in sel_cities:
                ser = city_data[city].loc[start_ts:end_ts]["AQI_PM"].dropna()
                val = float(ser.iloc[-1]) if not ser.empty else np.nan
                latest.append(dict(city=city, AQI_PM=np.round(val, 1), Category=aqi_label(val)))
                st.dataframe(pd.DataFrame(latest), use_container_width=True)
    except Exception as e:
        with st.expander("⚠️ AQI section failed"):
            st.exception(e)
            st.text(traceback.format_exc())

# ---- Sidebar footer
st.sidebar.markdown("---")
st.sidebar.caption(
    "Tip: refresh data with:\n"
    "`python run_pipeline.py --cities milan,paris,berlin --timestamp`"
)
