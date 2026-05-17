from rest_framework import generics, permissions

from apps.plots.models import AnalyticsSnapshot
from apps.users.models import User
from .serializers import AdminUserSerializer, AnalyticsSnapshotSerializer


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all().order_by('-date_joined')


class AdminUserDetailView(generics.UpdateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    http_method_names = ['patch']


class AdminAnalyticsView(generics.ListAPIView):
    serializer_class = AnalyticsSnapshotSerializer
    permission_classes = [IsAdmin]
    queryset = AnalyticsSnapshot.objects.all().order_by('-date')[:30]
