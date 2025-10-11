import argparse, pandas as pd

def daily_mean(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date","value"]).sort_values("date")
    daily = (df.set_index("date")["value"].resample("D").mean()
             .to_frame("value").reset_index())
    unit = df["unit"].mode().iloc[0] if "unit" in df and not df["unit"].dropna().empty else ""
    daily["unit"] = unit
    return daily

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    args = ap.parse_args()
    raw = pd.read_csv(args.inp)
    daily_mean(raw).to_csv(args.out, index=False)
    print(f"Saved daily mean: {args.out}")
