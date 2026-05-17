import pytest
from django.contrib.gis.geos import Point


MOCK_CARDS = [
    {'activity': 'spray', 'status': 'green', 'title': 'Good spray day', 'reason': 'Low wind.'},
    {'activity': 'irrigate', 'status': 'amber', 'title': 'Hold irrigation', 'reason': 'Rain coming.'},
    {'activity': 'plant', 'status': 'green', 'title': 'Good planting', 'reason': 'Warm and dry.'},
    {'activity': 'harvest', 'status': 'red', 'title': 'Avoid harvesting', 'reason': 'High humidity.'},
]


@pytest.mark.django_db
def test_recommendations_endpoint_returns_cards(auth_client, farmer, mocker):
    from apps.plots.models import Plot
    plot = Plot.objects.create(owner=farmer, name='Test', geometry=Point(28.0, -26.0))
    mocker.patch('apps.recommendations.views.get_recommendations', return_value=MOCK_CARDS)
    resp = auth_client.get(f'/api/plots/{plot.id}/recommendations/')
    assert resp.status_code == 200
    assert len(resp.data) == 4
    assert resp.data[0]['activity'] == 'spray'


@pytest.mark.django_db
def test_recommendations_endpoint_rejects_other_users_plot(auth_client, admin_user):
    from apps.plots.models import Plot
    plot = Plot.objects.create(owner=admin_user, name='Admin Plot', geometry=Point(28.0, -26.0))
    resp = auth_client.get(f'/api/plots/{plot.id}/recommendations/')
    assert resp.status_code == 404
