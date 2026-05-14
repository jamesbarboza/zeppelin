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
