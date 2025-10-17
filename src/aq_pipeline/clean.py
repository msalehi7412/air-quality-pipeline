import pandas as pd
from pathlib import Path
from .utils import get_logger, ensure_parent

def clean_daily(in_csv, out_csv, interpolate=True):
    log = get_logger()
    df = pd.read_csv(in_csv, parse_dates=["time"]).set_index("time").sort_index()
    if interpolate:
        df = df.interpolate(method="time", limit_area="inside")
    daily = df.resample("1D").mean(numeric_only=True)
    daily.index.name = "date"

    out = ensure_parent(out_csv)
    daily.to_csv(out)
    log.info(f"Saved daily means → {out}")
    return out
