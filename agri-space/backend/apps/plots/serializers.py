import json

from django.contrib.gis.geos import GEOSGeometry
from rest_framework import serializers

from .models import CropTag, Plot


class CropTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropTag
        fields = ['id', 'name', 'category']


class PlotSerializer(serializers.ModelSerializer):
    crop_tags = CropTagSerializer(many=True, read_only=True)
    crop_tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CropTag.objects.all(), write_only=True,
        source='crop_tags', required=False
    )
    geometry = serializers.JSONField()

    class Meta:
        model = Plot
        fields = ['id', 'name', 'geometry', 'area_hectares', 'crop_tags',
                  'crop_tag_ids', 'created_at']
        read_only_fields = ['id', 'area_hectares', 'created_at']

    def validate_geometry(self, value):
        try:
            geom = GEOSGeometry(json.dumps(value))
            if geom.geom_type not in ('Point', 'Polygon'):
                raise serializers.ValidationError('geometry must be a Point or Polygon')
            return geom
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(f'Invalid geometry: {e}')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['geometry'] = json.loads(instance.geometry.geojson)
        return data
