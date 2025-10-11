import argparse, requests, pandas as pd
BASE = "https://api.openaq.org/v2"

def get(endpoint, **params):
    r = requests.get(f"{BASE}/{endpoint}", params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("results", [])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", default="IT")
    ap.add_argument("--city_like", default=None, help="substring to search (e.g. Milan)")
    ap.add_argument("--limit", type=int, default=1000)
    args = ap.parse_args()

    # 1) What parameters exist in this country?
    params = pd.DataFrame(get("parameters", country=args.country, limit=args.limit))
    if not params.empty:
        print("\nParameters in country:", args.country)
        print(params[["id","name","displayName"]].head(20).to_string(index=False))

    # 2) List cities
    cities = pd.DataFrame(get("cities", country=args.country, limit=args.limit))
    if not cities.empty:
        if args.city_like:
            cities = cities[cities["city"].str.contains(args.city_like, case=False, na=False)]
        print("\nCities:")
        print(cities[["city","country","locations","count"]].head(50).to_string(index=False))

    # 3) List locations (sensors) for those cities (or whole country if not filtered)
    loc_params = {"country": args.country, "limit": args.limit}
    locs = pd.DataFrame(get("locations", **loc_params))
    if not locs.empty:
        if args.city_like:
            locs = locs[locs["city"].str.contains(args.city_like, case=False, na=False)]
        print("\nLocations (first 30):")
        cols = ["id","name","city","country","coordinates.latitude","coordinates.longitude","parameters"]
        cols = [c for c in cols if c in locs.columns]
        print(locs[cols].head(30).to_string(index=False))
        print("\nTip: use one of these location IDs with the fetch script.")

if __name__ == "__main__":
    main()
