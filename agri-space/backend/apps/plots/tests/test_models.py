import pytest
from django.contrib.gis.geos import Point, Polygon


@pytest.mark.django_db
def test_crop_tag_str(db):
    from apps.plots.models import CropTag
    tag = CropTag.objects.create(name='Maize', category='row_crop')
    assert str(tag) == 'Maize'


@pytest.mark.django_db
def test_plot_with_point_geometry_has_no_area(farmer):
    from apps.plots.models import Plot
    plot = Plot.objects.create(
        owner=farmer, name='Test Field', geometry=Point(28.0, -26.0)
    )
    assert plot.area_hectares is None


@pytest.mark.django_db
def test_plot_with_polygon_computes_area(farmer):
    from apps.plots.models import Plot
    # Small polygon ~0.5 ha
    poly = Polygon(((28.0, -26.0), (28.005, -26.0), (28.005, -26.005),
                    (28.0, -26.005), (28.0, -26.0)))
    plot = Plot.objects.create(owner=farmer, name='Poly Field', geometry=poly)
    assert plot.area_hectares is not None
    assert plot.area_hectares > 0


@pytest.mark.django_db
def test_weather_cache_rounds_coordinates():
    from apps.plots.models import WeatherCache
    cache = WeatherCache.objects.create(
        latitude=28.12345, longitude=-26.67890, forecast_json={}
    )
    assert cache.latitude == 28.12
    assert cache.longitude == -26.68


@pytest.mark.django_db
def test_weather_cache_sets_expires_at():
    from apps.plots.models import WeatherCache
    from django.utils import timezone
    before = timezone.now()
    cache = WeatherCache.objects.create(
        latitude=28.0, longitude=-26.0, forecast_json={}
    )
    after = timezone.now()
    assert cache.expires_at is not None
    assert before < cache.expires_at < after + timezone.timedelta(hours=1, seconds=5)


@pytest.mark.django_db
def test_plot_geometry_change_to_point_clears_area(farmer):
    from apps.plots.models import Plot
    from django.contrib.gis.geos import Point, Polygon
    poly = Polygon(((28.0, -26.0), (28.005, -26.0), (28.005, -26.005),
                    (28.0, -26.005), (28.0, -26.0)))
    plot = Plot.objects.create(owner=farmer, name='Change Field', geometry=poly)
    assert plot.area_hectares is not None
    plot.geometry = Point(28.0, -26.0)
    plot.save()
    assert plot.area_hectares is None
