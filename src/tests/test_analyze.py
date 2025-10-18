# tests/test_analyze.py
import pandas as pd
from aq_pipeline.analyze import compute_metrics

def test_compute_metrics_basic():
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    df = pd.DataFrame({
        "pm2_5": [10, 12, 11, 13, 12, 14, 11, 13, 12, 15],
        "pm10":  [20, 18, 19, 21, 22, 20, 19, 22, 21, 23],
    }, index=idx)

    metrics = compute_metrics(df)
    assert "pm2_5" in metrics and "pm10" in metrics
    # coverage ~ 100%, mean/max exist, slope not None when enough points
    assert metrics["pm2_5"].coverage_pct == 100.0
    assert metrics["pm2_5"].mean is not None
    assert metrics["pm2_5"].max  is not None
    assert metrics["pm2_5"].trend_slope_per_day is not None
