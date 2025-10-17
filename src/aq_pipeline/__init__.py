"""aq_pipeline: core package for fetching, cleaning, and visualizing air-quality data."""
from .fetch import fetch_openmeteo
from .clean import clean_daily
from .analyze import compute_metrics
from .plot import plot_combined, plot_per_pollutant
from .report import write_summary_report
