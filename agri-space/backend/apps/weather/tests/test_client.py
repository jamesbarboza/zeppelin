import pytest
import httpx


def test_fetch_forecast_returns_daily_variables(respx_mock):
    from apps.weather.client import fetch_forecast, DAILY_VARIABLES

    mock_response = {
        'latitude': -26.0, 'longitude': 28.0,
        'daily': {var: [0.0] * 7 for var in DAILY_VARIABLES},
        'daily_units': {var: 'mm' for var in DAILY_VARIABLES},
    }
    respx_mock.get('https://api.open-meteo.com/v1/forecast').mock(
        return_value=httpx.Response(200, json=mock_response)
    )
    result = fetch_forecast(-26.0, 28.0)
    assert 'daily' in result
    for var in DAILY_VARIABLES:
        assert var in result['daily']
