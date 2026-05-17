from rest_framework import serializers

from apps.plots.models import AnalyticsSnapshot
from apps.users.models import User


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'farm_name', 'role', 'is_active', 'date_joined']
        read_only_fields = ['id', 'email', 'farm_name', 'role', 'date_joined']


class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSnapshot
        fields = '__all__'
