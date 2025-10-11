import argparse, time, requests, pandas as pd
from config import SETTINGS

def fetch_once(params):
    r = requests.get(SETTINGS.base_url, params=params, timeout=SETTINGS.timeout)
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code} | params={params} | msg={r.text[:300]}")
    data = r.json().get("results", [])
    return pd.json_normalize(data, sep=".") if data else pd.DataFrame()

def fetch_all(city, parameter, limit=1000, pages=5, sleep=0.3):
    variants = [
        {"city": city, "parameter": parameter, "limit": limit},
        {"city": city, "parameter": parameter, "limit": limit, "country": "IT"},
        {"city": "Milano", "parameter": parameter, "limit": limit, "country": "IT"},
        {"parameter": parameter, "limit": limit, "country": "IT"},
    ]
    frames = []
    for v in variants:
        for p in range(1, pages + 1):
            q = dict(v, page=p)
            try:
                df = fetch_once(q)
            except Exception as e:
                if p == 1:
                    break
                else:
                    raise
            if df.empty:
                break
            frames.append(df)
            time.sleep(sleep)
        if frames:
            break
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def simplify(df):
    keep = {
        "date.local": "date",
        "value": "value",
        "unit": "unit",
        "coordinates.latitude": "lat",
        "coordinates.longitude": "lon",
        "city": "city",
        "parameter": "parameter",
    }
    for k in keep:
        if k not in df.columns:
            df[k] = None
    slim = df[list(keep)].rename(columns=keep)
    slim["date"] = pd.to_datetime(slim["date"], errors="coerce")
    return slim.dropna(subset=["date", "value"])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", default=SETTINGS.default_city)
    ap.add_argument("--parameter", default=SETTINGS.default_parameter)
    ap.add_argument("--limit", type=int, default=SETTINGS.default_limit)
    ap.add_argument("--pages", type=int, default=5)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    df = fetch_all(args.city, args.parameter, args.limit, args.pages)
    if df.empty:
        raise SystemExit(
            "No data returned after trying multiple query variants. "
            "Try another city (e.g., --city Rome) or parameter (pm10/no2)."
        )
    simplify(df).to_csv(args.out, index=False)
    print(f"Saved {args.out} | rows={len(df)}")
