import argparse
import requests
import pandas as pd

BASE = "https://air-quality-api.open-meteo.com/v1/air-quality"

# map short aliases -> API fields
PARAM_MAP = {
    "pm25": "pm2_5",
    "pm10": "pm10",
    "no2":  "nitrogen_dioxide",
    "co":   "carbon_monoxide",
    "o3":   "ozone",
    "so2":  "sulphur_dioxide",
}

def fetch_hourly_multi(lat, lon, parameters, date_from=None, date_to=None):
    api_fields = [PARAM_MAP[p] for p in parameters]
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(api_fields),
        "timezone": "auto",
    }
    if date_from: params["start_date"] = date_from
    if date_to:   params["end_date"]   = date_to

    r = requests.get(BASE, params=params, timeout=30)
    r.raise_for_status()
    j = r.json()
    hours = j.get("hourly", {})
    times = hours.get("time", [])
    units = j.get("hourly_units", {})

    # build wide df then melt to long (date, parameter, value)
    wide = pd.DataFrame({"date": pd.to_datetime(times, errors="coerce")})
    for p in parameters:
        field = PARAM_MAP[p]
        wide[p] = hours.get(field, [None] * len(times))

    df_long = wide.melt(id_vars="date", var_name="parameter", value_name="value")
    df_long["unit"] = df_long["parameter"].map({
        k: units.get(v, "") for k, v in PARAM_MAP.items()
    })
    df_long["lat"] = lat
    df_long["lon"] = lon
    df_long = df_long.dropna(subset=["date"]).sort_values(["parameter","date"])
    return df_long

if __name__ == "__main__":
    from datetime import date, timedelta

    ap = argparse.ArgumentParser(description="Fetch hourly air quality for multiple pollutants.")
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument(
        "--parameters",
        default="pm25,pm10,no2,co",
        help="comma-separated list from: pm25,pm10,no2,co,o3,so2",
    )
    ap.add_argument("--date_from", default=None, help="YYYY-MM-DD")
    ap.add_argument("--date_to",   default=None, help="YYYY-MM-DD")
    ap.add_argument("--out", required=True, help="CSV path")
    args = ap.parse_args()

    # sensible defaults: last 90 days to today
    if not args.date_to:
        args.date_to = date.today().strftime("%Y-%m-%d")
    if not args.date_from:
        args.date_from = (date.today() - timedelta(days=90)).strftime("%Y-%m-%d")

    # validate list
    wanted = [p.strip().lower() for p in args.parameters.split(",") if p.strip()]
    bad = [p for p in wanted if p not in PARAM_MAP]
    if bad:
        raise SystemExit(f"Unsupported parameters: {bad}. Allowed: {list(PARAM_MAP.keys())}")

    df = fetch_hourly_multi(args.lat, args.lon, wanted, args.date_from, args.date_to)
    if df.empty:
        raise SystemExit("No data returned.")
    df.to_csv(args.out, index=False)
    print(f"Saved {args.out} | rows={len(df)} | parameters={wanted}")
