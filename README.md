# 🌍 Air Quality Analysis Pipeline
*Updated: Oct, 2025*

A modular Python pipeline for **environmental data collection, cleaning, and visualization** using real-time data from the [Open-Meteo Air Quality API](https://open-meteo.com/).  
It fetches hourly air pollutant data (PM2.5, PM10, NO₂, CO, etc.), aggregates it into daily averages, and produces **combined and per-pollutant visualizations**.

---

## 🚀 Features
- 📡 **Automated Data Fetching** – via Open-Meteo API for any latitude/longitude.
- 🧹 **Data Cleaning & Interpolation** – daily resampling with optional gap interpolation.
- 📊 **Multi-Pollutant Visualization** – generates one combined plot and separate plots per pollutant.
- 📈 **Daily Reports** – summary statistics (min, max, mean, count) written to text files.
- 🧩 **Modular Design** – fetch, clean, and plot scripts work independently for easy reuse.

---

## 🗂 Project Structure


air-quality-pipeline/
│
├── data/
│ ├── raw/ # Raw hourly data from API
│ ├── processed/ # Cleaned, daily-mean datasets
│
├── figures/ # Output plots (combined + per pollutant)
├── reports/ # Summary reports
│
├── src/
│ ├── fetch_openmeteo.py # Fetches multi-pollutant hourly data
│ ├── clean_airquality.py # Cleans & resamples data to daily averages
│ ├── quick_plot.py # Generates combined + per-pollutant plots
│
├── requirements.txt
└── README.md


---

## ⚙️ Setup

### 1️⃣ Clone this repository
```bash
git clone https://github.com/msalehi7412/air-quality-pipeline.git
cd air-quality-pipeline

2️⃣ Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux

3️⃣ Install dependencies
pip install -r requirements.txt

📦 Usage
Step 1 — Fetch Data
python src/fetch_openmeteo.py --lat 45.4642 --lon 9.1900 --parameters pm25,pm10,no2,co --out data/raw/milan_multi.csv

Step 2 — Clean & Aggregate
python src/clean_airquality.py --in data/raw/milan_multi.csv --out data/processed/milan_multi_daily.csv --interpolate

Step 3 — Plot & Report
python src/quick_plot.py --in data/processed/milan_multi_daily.csv --out figures/milan_multi_daily_combined.png --report reports/milan_multi_daily.txt --separate_dir figures/per_pollutant


Outputs:

Combined plot → figures/milan_multi_daily_combined.png

Individual plots → figures/per_pollutant/*.png

Report → reports/milan_multi_daily.txt

📊 Example Output
Combined Plot	Per-Pollutant Example

	
🧠 Key Learnings

Using REST APIs for environmental data.

Building a modular, reproducible data pipeline.

Handling missing time-series data with Pandas interpolation.

Automating multi-pollutant visualization and analysis.

🔧 Technologies

Python 3.13

Pandas / Matplotlib

Requests (API access)

Argparse (CLI interface)

Open-Meteo Air Quality API

👨‍💻 Author

Masoud Salehi
Environmental Data Analyst
GitHub

📄 License

This project is licensed under the MIT License. See LICENSE for details.


---

## 💾 Step 3: Save the file
- Press **Ctrl + S** (or **Cmd + S** on Mac)  
- You should now see `README.md` appear in your file list (left panel).

---

## 🧱 Step 4: Commit and push to GitHub
In the VS Code terminal, run these commands **exactly**:

```powershell
git add README.md
git commit -m "Add README with setup, usage, and project overview"
git push origin main