# ================================
# Air Quality Pipeline Runner
# Author: [Your Name]
# Description: Fetch, clean, and visualize air-quality data automatically
# ================================

# --- Parameters ---
# Default: Milan
$lat = 45.4642
$lon = 9.1900
$city = "milan"
$parameters = "pm25,pm10,no2,co"

# --- Paths ---
$rawFile = "data/raw/${city}_multi.csv"
$cleanFile = "data/processed/${city}_multi_daily.csv"
$figCombined = "figures/${city}_multi_daily_combined.png"
$figDir = "figures/per_pollutant"
$reportFile = "reports/${city}_multi_daily.txt"

# --- Create folders if missing ---
Write-Host "📁 Checking folders..."
mkdir data/raw -ErrorAction SilentlyContinue
mkdir data/processed -ErrorAction SilentlyContinue
mkdir figures -ErrorAction SilentlyContinue
mkdir reports -ErrorAction SilentlyContinue
mkdir $figDir -ErrorAction SilentlyContinue

# --- Step 1: Fetch data ---
Write-Host "🌍 Fetching air-quality data from Open-Meteo..."
python src/fetch_openmeteo.py --lat $lat --lon $lon --parameters $parameters --out $rawFile

# --- Step 2: Clean data ---
Write-Host "🧹 Cleaning and aggregating data..."
python src/clean_airquality.py --in $rawFile --out $cleanFile --interpolate

# --- Step 3: Visualize ---
Write-Host "📊 Generating plots and reports..."
python src/quick_plot.py --in $cleanFile --out $figCombined --report $reportFile --separate_dir $figDir

# --- Finish ---
Write-Host "✅ Pipeline complete!"
Write-Host "   ➤ Raw data: $rawFile"
Write-Host "   ➤ Cleaned data: $cleanFile"
Write-Host "   ➤ Figures: $figCombined and $figDir"
Write-Host "   ➤ Report: $reportFile"
