from django.urls import path

from .views import AdminAnalyticsView, AdminUserDetailView, AdminUserListView

urlpatterns = [
    path('users/', AdminUserListView.as_view()),
    path('users/<uuid:pk>/', AdminUserDetailView.as_view()),
    path('analytics/', AdminAnalyticsView.as_view()),
]
