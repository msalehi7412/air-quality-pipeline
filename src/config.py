from dataclasses import dataclass

@dataclass
class Settings:
    base_url: str = "https://api.openaq.org/v2/measurements"
    default_city: str = "Milan"
    default_parameter: str = "pm25"
    default_limit: int = 1000
    timeout: int = 30

SETTINGS = Settings()
CITIES = {
    "milan": {"lat": 45.4642, "lon": 9.1900},
    "monza": {"lat": 45.5845, "lon": 9.2746},
    "paris": {"lat": 48.8566, "lon": 2.3522},
    "berlin": {"lat": 52.5200, "lon": 13.4050},
    "rome": {"lat": 41.9028, "lon": 12.4964},
    "tehran": {"lat": 35.6892, "lon": 51.3890},
    "madrid": {"lat": 40.4168, "lon": -3.7038},
}
