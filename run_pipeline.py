# run_pipeline.py — Orchestrates the full air-quality pipeline
from __future__ import annotations

# Make 'src/' importable when running from repo root
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import argparse
import logging
from datetime import date
from pathlib import Path

from aq_pipeline.fetch import fetch_openmeteo
from aq_pipeline.clean import clean_daily
from aq_pipeline.plot import plot_combined, plot_per_pollutant
from aq_pipeline.report import write_summary_report
from aq_pipeline.utils import ensure_parent

CITY_LOOKUP = {
    "milan":   (45.4642, 9.1900),
    "paris":   (48.8566, 2.3522),
    "berlin":  (52.5200, 13.4050),
    "rome":    (41.9028, 12.4964),
    "tehran":  (35.6892, 51.3890),
    "madrid":  (40.4168, -3.7038),
}

def slugify(s: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in s.lower()).strip("_")

def make_paths(city_slug: str, timestamped: bool) -> dict[str, Path]:
    stamp = f"_{date.today().isoformat()}" if timestamped else ""
    paths = {
        "raw":        Path(f"data/raw/{city_slug}_multi{stamp}.csv"),
        "processed":  Path(f"data/processed/{city_slug}_daily{stamp}.csv"),
        "combined":   Path(f"figures/{city_slug}_daily_combined{stamp}.png"),
        "per_pol_dir":Path("figures/per_pollutant"),
        "report":     Path(f"reports/{city_slug}{stamp}.txt"),
    }
    for p in [paths["raw"], paths["processed"], paths["combined"], paths["report"]]:
        ensure_parent(p)
    paths["per_pol_dir"].mkdir(parents=True, exist_ok=True)
    return paths

def run_one_city(
    city_name: str | None,
    lat: float,
    lon: float,
    parameters: list[str],
    interpolate: bool,
    timestamped: bool,
    dpi: int,
    past_days: int,
    start: str | None,
    end: str | None,
):
    city_slug = slugify(city_name or f"{lat}_{lon}")
    paths = make_paths(city_slug, timestamped)

    logging.info(f"=== {city_name or city_slug}: FETCH ===")
    fetch_openmeteo(
        lat=lat,
        lon=lon,
        parameters=parameters,
        out_csv=paths["raw"],
        past_days=past_days,
        start_date=start,
        end_date=end,
    )

    logging.info(f"=== {city_name or city_slug}: CLEAN ===")
    clean_daily(in_csv=paths["raw"], out_csv=paths["processed"], interpolate=interpolate)

    logging.info(f"=== {city_name or city_slug}: PLOT & REPORT ===")
    plot_combined(paths["processed"], paths["combined"], dpi=dpi)
    plot_per_pollutant(paths["processed"], paths["per_pol_dir"], dpi=dpi)
    write_summary_report(paths["processed"], paths["report"], city=city_name)

    logging.info(
        f"Done: {city_name or city_slug} → {paths['processed']}, {paths['combined']}, {paths['report']}"
    )

def main():
    ap = argparse.ArgumentParser(
        description="Run the air-quality pipeline (fetch → clean → plot → report)."
    )
    group = ap.add_mutually_exclusive_group(required=False)
    group.add_argument("--city", help="Known city (milan, paris, tehran, ...).")
    group.add_argument("--cities", help="Comma-separated cities to run.")

    ap.add_argument("--lat", type=float, help="Latitude if not using --city.")
    ap.add_argument("--lon", type=float, help="Longitude if not using --city.")
    ap.add_argument("--parameters", default="pm25,pm10,no2,co",
                    help="Comma-separated pollutants (pm25,pm10,no2,co).")
    ap.add_argument("--no-interpolate", action="store_true",
                    help="Disable interpolation in cleaning.")
    ap.add_argument("--timestamp", action="store_true",
                    help="Append today's date to output filenames.")
    ap.add_argument("--dpi", type=int, default=150, help="Figure DPI.")

    # NEW: range controls
    ap.add_argument("--past-days", type=int, default=30,
                    help="How many past days to fetch (ignored if --start/--end provided).")
    ap.add_argument("--start", help="Start date YYYY-MM-DD (optional).")
    ap.add_argument("--end", help="End date YYYY-MM-DD (optional).")

    ap.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = ap.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    parameters = [p.strip() for p in args.parameters.split(",") if p.strip()]

    # Build list of targets
    targets: list[tuple[str | None, float, float]] = []
    if args.cities:
        for c in [x.strip().lower() for x in args.cities.split(",") if x.strip()]:
            if c in CITY_LOOKUP:
                lat, lon = CITY_LOOKUP[c]
                targets.append((c.title(), lat, lon))
            else:
                raise SystemExit(f"Unknown city '{c}'. Known: {', '.join(sorted(CITY_LOOKUP))}")
    elif args.city:
        c = args.city.strip().lower()
        if c not in CITY_LOOKUP:
            raise SystemExit(f"Unknown city '{c}'. Known: {', '.join(sorted(CITY_LOOKUP))}")
        lat, lon = CITY_LOOKUP[c]
        targets.append((args.city.title(), lat, lon))
    else:
        if args.lat is None or args.lon is None:
            raise SystemExit("Provide --city OR both --lat and --lon.")
        targets.append((None, args.lat, args.lon))

    for city_name, lat, lon in targets:
        run_one_city(
            city_name=city_name,
            lat=lat,
            lon=lon,
            parameters=parameters,
            interpolate=not args.no_interpolate,
            timestamped=args.timestamp,
            dpi=args.dpi,
            past_days=args.past_days,
            start=args.start,
            end=args.end,
        )

if __name__ == "__main__":
    main()
