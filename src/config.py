from dataclasses import dataclass

@dataclass
class Settings:
    base_url: str = "https://api.openaq.org/v2/measurements"
    default_city: str = "Milan"
    default_parameter: str = "pm25"
    default_limit: int = 1000
    timeout: int = 30

SETTINGS = Settings()
