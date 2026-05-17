import json
from datetime import timedelta

import anthropic
from django.utils import timezone

from apps.plots.models import Plot, WeatherCache
from apps.weather.client import fetch_forecast

TOOL_SCHEMA = {
    'name': 'submit_recommendations',
    'description': 'Submit agricultural activity recommendations based on weather forecast.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'recommendations': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'activity': {'type': 'string', 'enum': ['spray', 'irrigate', 'plant', 'harvest']},
                        'status': {'type': 'string', 'enum': ['green', 'amber', 'red']},
                        'title': {'type': 'string', 'maxLength': 80},
                        'reason': {'type': 'string', 'maxLength': 200},
                    },
                    'required': ['activity', 'status', 'title', 'reason'],
                },
                'minItems': 4,
                'maxItems': 4,
            }
        },
        'required': ['recommendations'],
    },
}

SYSTEM_PROMPT = (
    'You are an expert agronomist. Analyze the 7-day weather forecast and provide one '
    'recommendation card for each of the 4 activities: spray, irrigate, plant, harvest. '
    'status: green=good conditions, amber=caution/wait, red=do not proceed. '
    'title: max 10 words, action-oriented. reason: one clear sentence citing the key weather factor. '
    'Consider the hemisphere for seasonal context.'
)


def get_recommendations(plot: Plot) -> list[dict]:
    if plot.geometry.geom_type == 'Point':
        lat = round(plot.geometry.y, 2)
        lng = round(plot.geometry.x, 2)
    else:
        centroid = plot.geometry.centroid
        lat = round(centroid.y, 2)
        lng = round(centroid.x, 2)

    today = timezone.now().date().isoformat()

    cached = WeatherCache.objects.filter(
        latitude=lat, longitude=lng, expires_at__gt=timezone.now()
    ).first()

    if cached:
        data = cached.forecast_json
        if data.get('reco_date') == today and 'recommendations' in data:
            return data['recommendations']
        forecast = data
    else:
        forecast = fetch_forecast(lat, lng)
        cached, _ = WeatherCache.objects.update_or_create(
            latitude=lat, longitude=lng,
            defaults={'forecast_json': forecast},
        )

    crop_names = list(plot.crop_tags.values_list('name', flat=True))
    hemisphere = 'northern' if lat >= 0 else 'southern'

    try:
        cards = _call_llm(forecast, crop_names, hemisphere)
    except Exception:
        cards = _fallback_recommendations(forecast)

    cached.forecast_json = {**forecast, 'recommendations': cards, 'reco_date': today}
    cached.save(update_fields=['forecast_json'])
    return cards


def _call_llm(forecast: dict, crop_tags: list[str], hemisphere: str) -> list[dict]:
    client = anthropic.Anthropic()
    user_message = (
        f"Crops: {', '.join(crop_tags) if crop_tags else 'General'}\n"
        f"Hemisphere: {hemisphere}\nDate: {timezone.now().date().isoformat()}\n\n"
        f"Forecast:\n{json.dumps(forecast.get('daily', {}), indent=2)}"
    )
    response = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=[TOOL_SCHEMA],
        tool_choice={'type': 'tool', 'name': 'submit_recommendations'},
        messages=[{'role': 'user', 'content': user_message}],
    )
    for block in response.content:
        if block.type == 'tool_use' and block.name == 'submit_recommendations':
            return block.input['recommendations']
    raise ValueError('LLM did not call submit_recommendations')


def _fallback_recommendations(forecast: dict) -> list[dict]:
    daily = forecast.get('daily', {})
    precip = daily.get('precipitation_sum', [0] * 7)
    wind = daily.get('wind_speed_10m_max', [0] * 7)
    humidity = daily.get('relative_humidity_2m_max', [50] * 7)
    temp_min = daily.get('temperature_2m_min', [15] * 7)

    today_rain = precip[0] if precip else 0
    today_wind = wind[0] if wind else 0
    today_humidity = humidity[0] if humidity else 50
    tomorrow_rain = precip[1] if len(precip) > 1 else 0

    return [
        {
            'activity': 'spray',
            'status': 'red' if today_wind > 20 or today_rain > 0 else 'amber' if tomorrow_rain > 5 else 'green',
            'title': 'Check local conditions before spraying',
            'reason': 'Live weather data temporarily unavailable — verify wind and rain locally.',
        },
        {
            'activity': 'irrigate',
            'status': 'red' if today_rain > 10 else 'amber' if today_rain > 2 else 'green',
            'title': 'Check soil moisture before irrigating',
            'reason': 'Live weather data temporarily unavailable — check soil moisture manually.',
        },
        {
            'activity': 'plant',
            'status': 'red' if temp_min[0] < 2 else 'amber' if today_rain > 5 else 'green',
            'title': 'Check temperature before planting',
            'reason': 'Live weather data temporarily unavailable — verify frost risk locally.',
        },
        {
            'activity': 'harvest',
            'status': 'red' if today_rain > 0 or today_humidity > 85 else 'amber' if today_humidity > 70 else 'green',
            'title': 'Check humidity before harvesting',
            'reason': 'Live weather data temporarily unavailable — check humidity locally.',
        },
    ]
