import pytest
from django.contrib.gis.geos import Point


MOCK_FORECAST = {
    'daily': {
        'precipitation_sum': [0.0, 0.0, 8.0, 0.0, 0.0, 0.0, 0.0],
        'wind_speed_10m_max': [12.0, 15.0, 10.0, 8.0, 9.0, 11.0, 13.0],
        'relative_humidity_2m_max': [55.0, 60.0, 75.0, 50.0, 52.0, 58.0, 61.0],
        'soil_moisture_0_to_1cm': [0.2, 0.2, 0.3, 0.3, 0.25, 0.22, 0.2],
        'temperature_2m_min': [18.0, 17.0, 15.0, 16.0, 17.0, 18.0, 19.0],
        'temperature_2m_max': [28.0, 27.0, 22.0, 25.0, 26.0, 27.0, 28.0],
        'et0_fao_evapotranspiration': [4.5, 4.2, 3.0, 3.8, 4.0, 4.3, 4.5],
    }
}

MOCK_LLM_CARDS = [
    {'activity': 'spray', 'status': 'green', 'title': 'Good spraying conditions', 'reason': 'Low wind and no rain forecast today.'},
    {'activity': 'irrigate', 'status': 'amber', 'title': 'Caution: rain Wednesday', 'reason': 'Hold irrigation — 8mm rain expected in 48 hours.'},
    {'activity': 'plant', 'status': 'green', 'title': 'Good planting window', 'reason': 'Warm temperatures and adequate soil moisture.'},
    {'activity': 'harvest', 'status': 'green', 'title': 'Good harvest conditions', 'reason': 'Low humidity and dry conditions today.'},
]


@pytest.mark.django_db
def test_get_recommendations_returns_four_cards(farmer, mocker):
    from apps.recommendations.engine import get_recommendations
    from apps.plots.models import Plot

    plot = Plot.objects.create(owner=farmer, name='Test', geometry=Point(28.0, -26.0))
    mocker.patch('apps.recommendations.engine.fetch_forecast', return_value=MOCK_FORECAST)
    mocker.patch('apps.recommendations.engine._call_llm', return_value=MOCK_LLM_CARDS)

    cards = get_recommendations(plot)
    assert len(cards) == 4
    activities = {c['activity'] for c in cards}
    assert activities == {'spray', 'irrigate', 'plant', 'harvest'}


@pytest.mark.django_db
def test_get_recommendations_uses_weather_cache(farmer, mocker):
    from apps.recommendations.engine import get_recommendations
    from apps.plots.models import Plot, WeatherCache
    from django.utils import timezone
    from datetime import timedelta

    plot = Plot.objects.create(owner=farmer, name='Cached', geometry=Point(28.0, -26.0))
    cached_forecast = {**MOCK_FORECAST, 'recommendations': MOCK_LLM_CARDS,
                       'reco_date': timezone.now().date().isoformat()}
    WeatherCache.objects.create(latitude=-26.0, longitude=28.0,
                                forecast_json=cached_forecast,
                                expires_at=timezone.now() + timedelta(hours=1))

    fetch_mock = mocker.patch('apps.recommendations.engine.fetch_forecast')
    llm_mock = mocker.patch('apps.recommendations.engine._call_llm')

    cards = get_recommendations(plot)
    fetch_mock.assert_not_called()
    llm_mock.assert_not_called()
    assert len(cards) == 4


@pytest.mark.django_db
def test_fallback_used_when_llm_fails(farmer, mocker):
    from apps.recommendations.engine import get_recommendations
    from apps.plots.models import Plot

    plot = Plot.objects.create(owner=farmer, name='Fallback', geometry=Point(28.0, -26.0))
    mocker.patch('apps.recommendations.engine.fetch_forecast', return_value=MOCK_FORECAST)
    mocker.patch('apps.recommendations.engine._call_llm', side_effect=Exception('API down'))

    cards = get_recommendations(plot)
    assert len(cards) == 4
    for card in cards:
        assert card['status'] in ('green', 'amber', 'red')
        assert 'title' in card and 'reason' in card
