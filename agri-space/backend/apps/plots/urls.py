from django.urls import path
from .views import PlotListView

urlpatterns = [
    path('plots/', PlotListView.as_view()),
]
