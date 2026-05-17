from rest_framework import generics, permissions, viewsets

from .models import CropTag, Plot
from .serializers import CropTagSerializer, PlotSerializer


class PlotViewSet(viewsets.ModelViewSet):
    serializer_class = PlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Plot.objects.filter(owner=self.request.user).prefetch_related('crop_tags')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CropTagListView(generics.ListAPIView):
    serializer_class = CropTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CropTag.objects.all().order_by('name')
