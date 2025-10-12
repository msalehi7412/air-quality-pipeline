import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys


def _format_date_axis(ax):
    loc = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))


def _save_line_plot(df, title, y_label, out_path, dpi=150):
    print(f"[plot] saving: {out_path}")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 5))
    plt.plot(df["date"], df["value"])
    _format_date_axis(plt.gca())
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(y_label)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=dpi)
    plt.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Plot daily air-quality time series (combined + per-pollutant). "
                    "Input must be the *daily* CSV in long format: date, parameter, value[, unit]."
    )
    ap.add_argument("--in", dest="inp", required=True, help="Path to daily CSV (from clean step)")
    ap.add_argument("--out", dest="out_combined", required=True, help="Path to combined PNG")
    ap.add_argument("--report", required=True, help="Path to summary TXT")
    ap.add_argument("--separate_dir", default=None,
                    help="Folder to save per-pollutant PNGs (one file per parameter). If omitted, only combined is saved.")
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    print(f"[start] quick_plot.py")
    print(f"[args] in={args.inp}")
    print(f"[args] out_combined={args.out_combined}")
    print(f"[args] report={args.report}")
    print(f"[args] separate_dir={args.separate_dir}")

    # ---- read
    df = pd.read_csv(args.inp, parse_dates=["date"])
    print(f"[read] rows={len(df)} cols={list(df.columns)}")
    if df.empty:
        sys.exit("[error] input dataframe is empty.")
    for req in ("date", "parameter", "value"):
        if req not in df.columns:
            sys.exit(f"[error] missing required column: {req}")

    df = df.sort_values(["parameter", "date"])

    # unit map
    if "unit" in df and not df["unit"].dropna().empty:
        unit_map = (df.dropna(subset=["unit"])
                      .groupby("parameter")["unit"]
                      .agg(lambda s: s.mode().iloc[0] if not s.mode().empty else ""))
        default_unit = df["unit"].mode().iloc[0]
    else:
        unit_map = {}
        default_unit = "Value"

    # ---- combined plot
    print("[combined] plotting…")
    Path(args.out_combined).parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 5))
    for p, g in df.groupby("parameter"):
        if g.empty:
            print(f"[warn] parameter {p} has no data, skipping.")
            continue
        plt.plot(g["date"], g["value"], label=p.upper())

    _format_date_axis(plt.gca())
    plt.title("Daily Air Quality — Combined")
    plt.xlabel("Date")
    plt.ylabel(default_unit)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.out_combined, dpi=args.dpi)
    plt.close()
    print(f"[combined] saved: {args.out_combined}")

    # ---- per-parameter plots
    if args.separate_dir:
        sep_dir = Path(args.separate_dir)
        sep_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(args.out_combined).stem
        print(f"[separate] directory: {sep_dir}")

        for p, g in df.groupby("parameter"):
            if g.empty:
                continue
            unit = unit_map.get(p, default_unit)
            out_path = sep_dir / f"{stem}_{p}.png"
            _save_line_plot(
                g,
                title=f"Daily Air Quality — {p.upper()}",
                y_label=unit if unit else "Value",
                out_path=out_path,
                dpi=args.dpi,
            )

    # ---- report
    print("[report] writing summary…")
    summary = (
        df.groupby("parameter")["value"]
          .agg(count="count", mean="mean", min="min", max="max")
          .round(2)
          .to_string()
    )
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        f.write(f"Report for {args.inp}\n\n{summary}\n")
    print(f"[report] saved: {args.report}")
    print("[done] quick_plot.py")
