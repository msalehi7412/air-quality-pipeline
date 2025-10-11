import argparse, pandas as pd, matplotlib.pyplot as plt

def write_report(df, path):
    vals = df["value"].dropna().tolist()
    text = "No values." if not vals else (
        f"Observations: {len(vals)}\n"
        f"Mean: {sum(vals)/len(vals):.2f}\n"
        f"Min: {min(vals):.2f}\n"
        f"Max: {max(vals):.2f}\n"
    )
    with open(path, "w", encoding="utf-8") as f: f.write(text)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", default=None)
    ap.add_argument("--report", dest="report", default=None)
    args = ap.parse_args()

    df = pd.read_csv(args.inp, parse_dates=["date"])
    if args.out:
        plt.figure()
        plt.plot(df["date"], df["value"])
        plt.xlabel("Date")
        ylabel = df["unit"].iloc[0] if "unit" in df.columns and not df["unit"].isna().all() else "value"
        plt.ylabel(ylabel); plt.title("Daily Air Quality"); plt.tight_layout()
        plt.savefig(args.out, dpi=150); plt.close()
        print(f"Saved plot: {args.out}")
    if args.report:
        write_report(df, args.report); print(f"Saved report: {args.report}")
