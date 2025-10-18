# tests/test_report.py
import pandas as pd
from pathlib import Path
from aq_pipeline.report import write_summary_report

def test_write_summary_report(tmp_path: Path):
    csv = tmp_path / "daily.csv"
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=5, freq="D"),
        "pm2_5": [10, 11, 12, 13, 14],
        "pm10":  [20, 19, 21, 22, 23],
    })
    df.to_csv(csv, index=False)

    out = tmp_path / "report.txt"
    write_summary_report(csv, out, city="Testville")
    text = out.read_text(encoding="utf-8")
    assert out.exists()
    assert "Pollutant Summary" in text
    assert "Testville" in text
