from django.urls import path
from .views import RecommendationsView

urlpatterns = [
    path('plots/<uuid:plot_id>/recommendations/', RecommendationsView.as_view()),
]
