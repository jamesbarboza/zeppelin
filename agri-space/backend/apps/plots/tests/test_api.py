import pytest

POINT_GEOM = {'type': 'Point', 'coordinates': [28.0, -26.0]}
POLYGON_GEOM = {
    'type': 'Polygon',
    'coordinates': [[[28.0, -26.0], [28.005, -26.0], [28.005, -26.005],
                     [28.0, -26.005], [28.0, -26.0]]]
}


@pytest.mark.django_db
def test_create_plot_with_pin(auth_client):
    resp = auth_client.post('/api/plots/', {'name': 'North Field', 'geometry': POINT_GEOM}, format='json')
    assert resp.status_code == 201
    assert resp.data['name'] == 'North Field'
    assert resp.data['geometry']['type'] == 'Point'


@pytest.mark.django_db
def test_create_plot_with_polygon_computes_area(auth_client):
    resp = auth_client.post('/api/plots/', {'name': 'Poly Field', 'geometry': POLYGON_GEOM}, format='json')
    assert resp.status_code == 201
    assert resp.data['area_hectares'] is not None


@pytest.mark.django_db
def test_list_plots_returns_only_owners_plots(auth_client, farmer, admin_user):
    from apps.plots.models import Plot
    from django.contrib.gis.geos import Point
    Plot.objects.create(owner=farmer, name='Mine', geometry=Point(28.0, -26.0))
    Plot.objects.create(owner=admin_user, name='Theirs', geometry=Point(29.0, -27.0))
    resp = auth_client.get('/api/plots/')
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]['name'] == 'Mine'


@pytest.mark.django_db
def test_delete_plot(auth_client, farmer):
    from apps.plots.models import Plot
    from django.contrib.gis.geos import Point
    plot = Plot.objects.create(owner=farmer, name='Delete Me', geometry=Point(28.0, -26.0))
    resp = auth_client.delete(f'/api/plots/{plot.id}/')
    assert resp.status_code == 204


@pytest.mark.django_db
def test_cannot_access_other_users_plot(auth_client, admin_user):
    from apps.plots.models import Plot
    from django.contrib.gis.geos import Point
    plot = Plot.objects.create(owner=admin_user, name='Admin Plot', geometry=Point(28.0, -26.0))
    resp = auth_client.get(f'/api/plots/{plot.id}/')
    assert resp.status_code == 404


@pytest.mark.django_db
def test_list_crop_tags(auth_client):
    from apps.plots.models import CropTag
    CropTag.objects.create(name='Maize', category='row_crop')
    resp = auth_client.get('/api/crop-tags/')
    assert resp.status_code == 200
    assert any(t['name'] == 'Maize' for t in resp.data)
