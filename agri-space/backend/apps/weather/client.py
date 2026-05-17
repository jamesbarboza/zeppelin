import httpx

OPEN_METEO_URL = 'https://api.open-meteo.com/v1/forecast'

DAILY_VARIABLES = [
    'precipitation_sum',
    'wind_speed_10m_max',
    'relative_humidity_2m_max',
    'precipitation_probability_max',
    'temperature_2m_min',
    'temperature_2m_max',
    'et0_fao_evapotranspiration',
]


def fetch_forecast(lat: float, lng: float) -> dict:
    params = {
        'latitude': lat,
        'longitude': lng,
        'daily': ','.join(DAILY_VARIABLES),
        'forecast_days': 7,
        'timezone': 'auto',
    }
    response = httpx.get(OPEN_METEO_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
