# tests/test_utils.py
import pytest
from aq_pipeline.utils import validate_parameters, to_api_params

def test_validate_parameters_ok():
    assert validate_parameters(["pm25", "pm10", "no2", "co"]) == ["pm25", "pm10", "no2", "co"]

def test_validate_parameters_bad():
    with pytest.raises(ValueError):
        validate_parameters(["pm25", "o3"])  # o3 not in this project’s mapping

def test_to_api_params_mapping():
    assert to_api_params(["pm25", "pm10", "no2", "co"]) == [
        "pm2_5", "pm10", "nitrogen_dioxide", "carbon_monoxide"
    ]
