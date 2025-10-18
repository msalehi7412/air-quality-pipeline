Air Quality Pipeline & Dashboard

Modular Python pipeline to fetch → clean → analyze → visualize multi-pollutant air-quality data from the Open-Meteo Air Quality API. Includes a one-command orchestrator and a Streamlit dashboard for multi-city comparison.


✨ Features

Modular package: aq_pipeline/ (fetch, clean, analyze, plot, report)

CLI scripts: run each stage or the full pipeline

Orchestrator: run_pipeline.py (one command, one or many cities)

Streamlit dashboard: multi-city time series, KPIs, PM-based AQI

Metrics: coverage %, mean, max, p95, trend slope, anomalies (IQR)

Reproducibility: venv, requirements, deterministic outputs

Extensible: easily add cities via CITY_LOOKUP

🗂️ Project Structure
air-quality-pipeline/
├── src/
│   ├── aq_pipeline/
│   │   ├── __init__.py
│   │   ├── fetch.py        # Open-Meteo API (hourly → CSV)
│   │   ├── clean.py        # hourly → daily means (+interpolation)
│   │   ├── analyze.py      # metrics: coverage, p95, trend, anomalies
│   │   ├── plot.py         # combined & per-pollutant PNGs
│   │   ├── report.py       # text summary per run
│   │   └── utils.py        # logging, param mapping, helpers
│   └── dashboard_app.py    # Streamlit multi-city dashboard
├── run_pipeline.py          # one-command orchestrator
├── data/                    # (ignored) raw/processed CSVs
├── figures/                 # (ignored) generated plots
├── reports/                 # (ignored) text summaries
├── requirements.txt
└── README.md


Make sure .gitignore includes:

.venv/
__pycache__/
.ipynb_checkpoints/
data/
figures/
reports/

⚙️ Setup
# 1) Clone
git clone https://github.com/<you>/air-quality-pipeline.git
cd air-quality-pipeline

# 2) Create & activate venv
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 3) Install deps
pip install -r requirements.txt

🚀 Quickstart (One City)

Fetch the last 10 days for Milan, clean, analyze, plot, and write a report:

python run_pipeline.py --city milan --past-days 10 --timestamp


Backfill 5 months of real data:

# Windows PowerShell
$today  = (Get-Date).ToString('yyyy-MM-dd')
$start5 = (Get-Date).AddMonths(-5).ToString('yyyy-MM-dd')
python run_pipeline.py --city milan --start $start5 --end $today


Outputs go to:

data/raw/...
data/processed/...
figures/...
reports/...

🧭 Multi-City (One Command)
python run_pipeline.py --cities milan,paris,berlin,rome,tehran,madrid --start 2025-05-01 --end 2025-10-17


Add/remove cities in CITY_LOOKUP inside run_pipeline.py.

🧪 CLI Reference
python run_pipeline.py [--city CITY | --cities a,b,c] \
  [--lat LAT --lon LON] \
  [--parameters "pm25,pm10,no2,co"] \
  [--past-days N | --start YYYY-MM-DD --end YYYY-MM-DD] \
  [--no-interpolate] [--timestamp] [--dpi 150] [--log-level INFO]


--parameters (friendly names) are mapped to Open-Meteo fields:

pm25 → pm2_5, pm10 → pm10, no2 → nitrogen_dioxide, co → carbon_monoxide

📊 Streamlit Dashboard
streamlit run src/dashboard_app.py


Cities: pick one or many (auto-discovers latest processed CSV per city)

Date range: select any dates within the last 5 months (or the full backfilled span)

Tabs:

Time Series: daily pollutant lines

KPIs: mean, p95 (95th percentile), max

AQI (PM-based): overall AQI from PM₂.₅/PM₁₀ (US EPA breakpoints), latest category

If you see empty charts for some dates, backfill that date range with --start/--end (see Quickstart).

📈 What’s in the Report

Each run generates reports/<city>_*.txt with:

Date range

Per-pollutant: coverage%, mean, max, p95, trend slope (µg/m³/day), anomalies

Example:

City: Milan
Range: 2025-05-20 – 2025-10-17

Pollutant Summary (daily):
name | coverage% | mean | max | p95 | trend(µg/m³/day) | anomalies
pm2_5 | 98.6 | 13.42 | 48.10 | 32.50 | 0.012 | 3
pm10  | 98.6 | 22.51 | 77.22 | 46.10 | -0.005 | 2
...

🧰 Troubleshooting

“No data in this period”: you haven’t fetched that range yet. Run:

python run_pipeline.py --city CITY --start 2025-06-01 --end 2025-10-17


Streamlit black page: stop (Ctrl+C), clear cache streamlit cache clear, retry on a new port:

streamlit run src/dashboard_app.py --server.port 8502


ModuleNotFoundError: aq_pipeline when running from repo root:

You already have a fix at the top of run_pipeline.py that adds src/ to sys.path.

Or install the package in editable mode later via pyproject.toml.

🗺️ Roadmap (next)

WHO guideline bands & rolling 7/30-day lines in plots

EU/WHO AQI variants (include NO₂/CO)

GitHub Actions CI (tests) + CRON job (daily fetch)

Optional Dockerfile

📜 License

MIT (or your choice)

🙌 Acknowledgments

Data: Open-Meteo Air Quality API

Python: pandas, matplotlib, streamlit