from django.urls import path
from .views import (
    RegisterView, CookieTokenObtainPairView,
    CookieTokenRefreshView, LogoutView, MeView
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', CookieTokenObtainPairView.as_view()),
    path('refresh/', CookieTokenRefreshView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('me/', MeView.as_view()),
]
