import argparse
import requests
import pandas as pd

BASE = "https://air-quality-api.open-meteo.com/v1/air-quality"

PARAM_MAP = {
    "pm25": "pm2_5",
    "pm10": "pm10",
    "no2":  "nitrogen_dioxide",
    "o3":   "ozone",
    "so2":  "sulphur_dioxide"
}

def fetch_hourly(lat, lon, parameter, date_from=None, date_to=None):
    api_param = PARAM_MAP.get(parameter.lower())
    if not api_param:
        raise SystemExit(f"Unsupported parameter '{parameter}'. Use one of: {list(PARAM_MAP.keys())}")

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": api_param,
        "timezone": "auto"
    }
    if date_from: params["start_date"] = date_from
    if date_to:   params["end_date"]   = date_to

    r = requests.get(BASE, params=params, timeout=30)
    r.raise_for_status()
    j = r.json()

    # Parse hourly arrays
    hours = j.get("hourly", {})
    times = hours.get("time", [])
    values = hours.get(api_param, [])

    df = pd.DataFrame({"date": pd.to_datetime(times, errors="coerce"),
                       "value": values})
    df["unit"] = j.get("hourly_units", {}).get(api_param, "")
    df["lat"] = lat
    df["lon"] = lon
    df["city"] = ""
    df["parameter"] = parameter.lower()
    df = df.dropna(subset=["date", "value"])
    return df

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Fetch hourly air-quality from Open-Meteo and save as CSV")
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--parameter", default="pm25", help="pm25|pm10|no2|o3|so2")
    ap.add_argument("--date_from", default=None, help="YYYY-MM-DD")
    ap.add_argument("--date_to",   default=None, help="YYYY-MM-DD")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    df = fetch_hourly(args.lat, args.lon, args.parameter, args.date_from, args.date_to)
    if df.empty:
        raise SystemExit("No data returned for this location/parameter/date range.")
    df.to_csv(args.out, index=False)
    print(f"Saved {args.out} | rows={len(df)} | unit={df['unit'].iloc[0] if 'unit' in df.columns else ''}")
