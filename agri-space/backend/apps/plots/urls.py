from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CropTagListView, PlotViewSet

router = DefaultRouter()
router.register('plots', PlotViewSet, basename='plot')

urlpatterns = [
    path('', include(router.urls)),
    path('crop-tags/', CropTagListView.as_view()),
]
