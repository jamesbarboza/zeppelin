import uuid
from django.contrib.gis.db import models as gis_models
from django.db import models


class CropTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20,
        choices=[('row_crop', 'Row Crop'), ('horticulture', 'Horticulture'),
                 ('orchard', 'Orchard'), ('pasture', 'Pasture'), ('other', 'Other')],
        default='other',
    )

    def __str__(self):
        return self.name


class Plot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='plots')
    name = models.CharField(max_length=255)
    geometry = gis_models.GeometryField(srid=4326)
    area_hectares = models.FloatField(null=True, blank=True)
    crop_tags = models.ManyToManyField(CropTag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.geometry and self.geometry.geom_type == 'Polygon':
            projected = self.geometry.transform(3857, clone=True)
            self.area_hectares = projected.area / 10000
        super().save(*args, **kwargs)


class WeatherCache(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    latitude = models.FloatField()
    longitude = models.FloatField()
    fetched_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    forecast_json = models.JSONField()

    class Meta:
        unique_together = ['latitude', 'longitude']


class AnalyticsSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    total_users = models.IntegerField(default=0)
    active_users_7d = models.IntegerField(default=0)
    total_plots = models.IntegerField(default=0)
    recommendations_generated = models.IntegerField(default=0)
    top_crop_tags_json = models.JSONField(default=list)
