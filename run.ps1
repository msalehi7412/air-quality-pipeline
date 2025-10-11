# Fetch Milan PM2.5 (last 90 days), clean, plot, report
python src\fetch_openmeteo.py --lat 45.4642 --lon 9.1900 --parameter pm25 --date_from 2024-11-01 --date_to 2025-02-01 --out data\raw\milan_pm25.csv
python src\clean_airquality.py --in data\raw\milan_pm25.csv --out data\processed\milan_pm25_daily.csv
python src\quick_plot.py --in data\processed\milan_pm25_daily.csv --out figures\milan_pm25_daily.png --report reports\milan_pm25_daily.txt
