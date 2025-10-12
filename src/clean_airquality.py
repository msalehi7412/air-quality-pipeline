import argparse
import pandas as pd
from typing import Optional

def daily_mean(
    raw_df: pd.DataFrame,
    interpolate: bool = False,
    method: str = "linear",
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """
    Build a continuous daily series. Works with either:
      - single-parameter input (columns: date,value[,unit])
      - multi-parameter long format (date,parameter,value[,unit])
    Returns long format: date, parameter, value, unit
    """
    df = raw_df.copy()
    if "date" not in df or "value" not in df:
        raise ValueError("Input must contain 'date' and 'value'.")
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=False)
    df = df.dropna(subset=["date", "value"]).sort_values(["date"] + (["parameter"] if "parameter" in df else []))
    if df.empty:
        return pd.DataFrame(columns=["date","parameter","value","unit"])

    if "parameter" not in df:
        df["parameter"] = "value"

    # daily mean per parameter
    daily = (
        df.set_index("date")
          .groupby("parameter")["value"]
          .resample("D").mean()
          .reset_index()
    )

    # build continuous calendar per parameter
    out = []
    for p, g in daily.groupby("parameter", as_index=False):
        g = g.set_index("date")
        idx = pd.date_range(g.index.min().floor("D"), g.index.max().ceil("D"), freq="D")
        g = g.reindex(idx).rename_axis("date").reset_index()
        g["parameter"] = p
        out.append(g)
    daily = pd.concat(out, ignore_index=True)

    # unit column (mode per parameter if present)
    if "unit" in df and not df["unit"].dropna().empty:
        unit_map = df.groupby("parameter")["unit"].agg(lambda s: s.mode().iloc[0] if not s.mode().empty else "")
        daily["unit"] = daily["parameter"].map(unit_map).fillna("")
    else:
        daily["unit"] = ""

    if interpolate:
        daily["value"] = daily.groupby("parameter", group_keys=False)["value"].apply(
            lambda s: s.interpolate(
                method=method if method in ("linear","time") else "linear",
                limit=limit,
                limit_direction="both"
            )
        )
    return daily

def main():
    ap = argparse.ArgumentParser(description="Daily mean with continuous calendar (supports multiple pollutants).")
    ap.add_argument("--in", dest="inp", required=True, help="Path to raw CSV from fetch step")
    ap.add_argument("--out", dest="out", required=True, help="Path to write daily CSV")
    ap.add_argument("--interpolate", action="store_true")
    ap.add_argument("--interp_method", default="linear")
    ap.add_argument("--interp_limit", type=int, default=None)
    args = ap.parse_args()

    raw = pd.read_csv(args.inp)
    daily = daily_mean(raw, args.interpolate, args.interp_method, args.interp_limit)
    daily.to_csv(args.out, index=False)
    print(f"Saved daily mean: {args.out} | rows={len(daily)} | params={daily['parameter'].nunique()} | interpolate={args.interpolate}")

if __name__ == "__main__":
    main()
