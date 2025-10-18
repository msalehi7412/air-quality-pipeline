![CI](https://github.com/msalehi7412/air-quality-pipeline/actions/workflows/ci.yml/badge.svg)

# 🌍 Air Quality Pipeline — Multi-City AQI Dashboard

A modular Python project that **fetches, cleans, analyzes, and visualizes real-time air quality data**  
using the [Open-Meteo Air Quality API](https://open-meteo.com/).  
Includes an automated workflow, reproducible data pipeline, and an interactive **Streamlit dashboard**.

---

## 🧠 Project Overview

This project automates the end-to-end process of **air-quality monitoring and visualization** for multiple cities.

**Key features:**
- Fetches pollutants data (PM₂.₅, PM₁₀, NO₂, CO) from Open-Meteo API  
- Cleans and processes raw data into daily means  
- Generates pollutant trend visualizations and statistical summaries  
- Builds a multi-city AQI dashboard for interactive comparison  
- Automated **CI/CD testing pipeline** with GitHub Actions  
- Fully reproducible via command line or PowerShell scripts

---

## 🧩 Repository Structure

air-quality-pipeline/
├── src/
│ ├── aq_pipeline/
│ │ ├── fetch.py # Fetches data from API
│ │ ├── clean.py # Cleans and preprocesses data
│ │ ├── analyze.py # Calculates trends and stats
│ │ ├── plot.py # Creates pollutant trend visualizations
│ │ ├── report.py # Generates summary reports
│ │ └── utils.py # Helper functions
│ ├── dashboard_app.py # Streamlit dashboard
│ └── tests/ # Pytest unit tests
│
├── run_pipeline.py # Main orchestrator for CLI workflow
├── run.ps1 # Quick PowerShell runner
├── requirements.txt # Dependencies
├── .github/workflows/ci.yml # GitHub Actions workflow
├── LICENSE
└── README.md

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/msalehi7412/air-quality-pipeline.git
cd air-quality-pipeline
2️⃣ Create a virtual environment and install dependencies
```bash

python -m venv .venv
.\.venv\Scripts\Activate.ps1     # (Windows)
pip install -r requirements.txt
🚀 Usage
Option 1: Run the full pipeline (with date range)
Fetch and process air-quality data for the last 5 months across all cities:

```powershell

$today  = (Get-Date).ToString('yyyy-MM-dd')
$start5 = (Get-Date).AddMonths(-5).ToString('yyyy-MM-dd')

python run_pipeline.py --cities milan,paris,berlin,rome,tehran,madrid --start $start5 --end $today --timestamp
Outputs:

data/raw/ and data/processed/ → CSV data files

figures/ → pollutant plots

reports/ → summary text reports

Option 2: Launch the interactive dashboard
Visualize pollutant trends and AQI across cities:

```bash

streamlit run src/dashboard_app.py
Then open your browser at http://localhost:8501

📊 Example Dashboard Preview

(If you don’t have this image yet, take a screenshot of your dashboard and save it as
figures/demo_dashboard.png to display it here.)

🧪 Testing (CI/CD)
This project uses Pytest for unit testing and GitHub Actions for continuous integration.

Run tests locally:

```bash

pytest -q src/tests
Each push or pull request automatically runs these tests in CI:

```yaml

.github/workflows/ci.yml
🧠 Tech Stack
Category	Tools
Programming	Python (3.12)
Data Handling	Pandas, NumPy
Visualization	Matplotlib, Streamlit
Automation	CLI workflow, PowerShell, argparse
Testing	Pytest, GitHub Actions
Data Source	Open-Meteo Air Quality API

🧩 Example Insights
Milan and Tehran showed higher PM₂.₅ variability over the last months.

Paris and Berlin maintain relatively stable pollutant levels.

Carbon monoxide peaks correlated with cooler months and reduced wind speed.

📈 Continuous Integration
The CI pipeline automatically:

Installs dependencies

Runs all unit tests (pytest src/tests)

Reports pass/fail status on GitHub PRs

You can view the latest run in the Actions tab.

📄 License
Licensed under the MIT License — free to use and modify.

👨‍💻 Author
Masoud Salehi
🌐 LinkedIn
📧 masoudsalehi7412@gmail.com
🔗 GitHub