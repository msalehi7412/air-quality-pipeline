# src/aq_pipeline/plot.py
from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from .utils import get_logger, ensure_parent


def plot_combined(
    daily_csv: str | Path,
    out_png: str | Path,
    title: str = "Daily Air Quality Means",
    dpi: int = 150,
) -> Path:
    """Plot all pollutants together from a daily CSV."""
    log = get_logger()
    df = pd.read_csv(daily_csv, parse_dates=["date"]).set_index("date")

    ax = df.plot(figsize=(10, 5))
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Concentration (µg/m³)")

    out = ensure_parent(out_png)
    plt.tight_layout()
    plt.savefig(out, dpi=dpi)
    plt.close()
    log.info(f"Saved combined plot → {out}")
    return out


def plot_per_pollutant(
    daily_csv: str | Path,
    out_dir: str | Path,
    prefix: str = "",
    dpi: int = 150,
) -> list[Path]:
    """Plot one figure per pollutant into out_dir."""
    log = get_logger()
    df = pd.read_csv(daily_csv, parse_dates=["date"]).set_index("date")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for col in df.columns:
        ax = df[col].plot(figsize=(8, 4))
        ax.set_title(f"{prefix}{col} — Daily Mean")
        ax.set_xlabel("Date")
        ax.set_ylabel("Concentration (µg/m³)")

        p = out_dir / f"{prefix}{col}.png"
        plt.tight_layout()
        plt.savefig(p, dpi=dpi)
        plt.close()
        log.info(f"Saved {col} → {p}")
        paths.append(p)

    return paths
