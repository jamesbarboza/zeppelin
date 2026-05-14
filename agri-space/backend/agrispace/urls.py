from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('apps.users.urls')),
    path('api/', include('apps.plots.urls')),
    path('api/', include('apps.recommendations.urls')),
    path('api/admin/', include('apps.admin_panel.urls')),
]
