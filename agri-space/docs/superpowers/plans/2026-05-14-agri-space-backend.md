# Agri-Space Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Django REST API backend for the Agri-Space agricultural weather recommendation platform.

**Architecture:** Django 5 + DRF with a custom User model, PostGIS for plot geometries, Open-Meteo for weather data, and Claude Haiku via the Anthropic SDK for LLM-powered activity recommendations. JWT auth stored in httpOnly cookies.

**Tech Stack:** Python 3.11+, Django 5.0, djangorestframework 3.15, djangorestframework-simplejwt 5.3, psycopg2-binary, django.contrib.gis + PostGIS, anthropic SDK, httpx, pytest, pytest-django.

---

## Prerequisites

Before starting:
1. PostgreSQL 15+ with PostGIS extension available: `CREATE EXTENSION postgis;`
2. GDAL system library: `brew install gdal` (macOS) or `apt install libgdal-dev` (Ubuntu)
3. Python 3.11+
4. An Anthropic API key (set in `.env` as `ANTHROPIC_API_KEY`)

---

## File Map

```
backend/
  requirements.txt
  .env.example
  pytest.ini
  conftest.py
  manage.py
  agrispace/
    __init__.py
    settings.py
    urls.py
    wsgi.py
    authentication.py          # CookieJWTAuthentication
  apps/
    users/
      __init__.py
      models.py                # Custom User (email login, role field)
      serializers.py           # RegisterSerializer, UserSerializer
      views.py                 # RegisterView, CookieTokenObtainPairView, CookieTokenRefreshView
      urls.py
      tests/
        __init__.py
        test_auth.py
    plots/
      __init__.py
      models.py                # CropTag, Plot, WeatherCache, AnalyticsSnapshot
      serializers.py           # CropTagSerializer, PlotSerializer
      views.py                 # PlotViewSet, CropTagListView
      urls.py
      management/
        commands/
          snapshot_analytics.py
      tests/
        __init__.py
        test_models.py
        test_api.py
    weather/
      __init__.py
      client.py                # fetch_forecast(lat, lng) -> dict
      tests/
        __init__.py
        test_client.py
    recommendations/
      __init__.py
      engine.py                # get_recommendations(plot) -> list[dict]
      views.py                 # RecommendationsView
      urls.py
      tests/
        __init__.py
        test_engine.py
        test_api.py
    admin_panel/
      __init__.py
      serializers.py           # AdminUserSerializer, AnalyticsSerializer
      views.py                 # AdminUserListView, AdminUserDetailView, AdminAnalyticsView
      urls.py
      tests/
        __init__.py
        test_api.py
```

---

## Task 1: Project Scaffold

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/pytest.ini`
- Create: `backend/conftest.py`
- Create: `backend/agrispace/settings.py`
- Create: `backend/agrispace/urls.py`
- Create: `backend/agrispace/authentication.py`

- [ ] **Step 1: Create the backend directory and install Django**

```bash
mkdir -p backend && cd backend
python -m venv venv && source venv/bin/activate
pip install Django==5.0.6 djangorestframework==3.15.2 djangorestframework-simplejwt==5.3.1 \
  django-cors-headers==4.4.0 psycopg2-binary==2.9.9 \
  anthropic==0.40.0 httpx==0.27.0 python-dotenv==1.0.1 \
  pytest==8.3.2 pytest-django==4.9.0 pytest-mock==3.14.0 model-bakery==1.20.0
pip freeze > requirements.txt
django-admin startproject agrispace .
mkdir -p apps/users apps/plots apps/weather apps/recommendations apps/admin_panel
touch apps/__init__.py apps/users/__init__.py apps/plots/__init__.py \
  apps/weather/__init__.py apps/recommendations/__init__.py apps/admin_panel/__init__.py
mkdir -p apps/users/tests apps/plots/tests apps/plots/management/commands \
  apps/weather/tests apps/recommendations/tests apps/admin_panel/tests
touch apps/users/tests/__init__.py apps/plots/tests/__init__.py \
  apps/weather/tests/__init__.py apps/recommendations/tests/__init__.py \
  apps/admin_panel/tests/__init__.py apps/plots/management/__init__.py \
  apps/plots/management/commands/__init__.py
```

- [ ] **Step 2: Write `.env.example`**

```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgis://agrispace:password@localhost:5432/agrispace
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Copy to `.env` and fill in real values.

- [ ] **Step 3: Write `agrispace/settings.py`**

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'apps.users',
    'apps.plots',
    'apps.weather',
    'apps.recommendations',
    'apps.admin_panel',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agrispace.urls'
WSGI_APPLICATION = 'agrispace.wsgi.application'

TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
               'DIRS': [], 'APP_DIRS': True,
               'OPTIONS': {'context_processors': [
                   'django.template.context_processors.debug',
                   'django.template.context_processors.request',
                   'django.contrib.auth.context_processors.auth',
                   'django.contrib.messages.context_processors.messages',
               ]}}]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_NAME', 'agrispace'),
        'USER': os.getenv('DB_USER', 'agrispace'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'agrispace.authentication.CookieJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
CORS_ALLOW_CREDENTIALS = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_TZ = True
```

- [ ] **Step 4: Write `agrispace/authentication.py`**

```python
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('access_token')
        if not token:
            return None
        try:
            validated_token = self.get_validated_token(token)
            return self.get_user(validated_token), validated_token
        except InvalidToken:
            return None
```

- [ ] **Step 5: Write `agrispace/urls.py`**

```python
from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('apps.users.urls')),
    path('api/', include('apps.plots.urls')),
    path('api/', include('apps.recommendations.urls')),
    path('api/admin/', include('apps.admin_panel.urls')),
]
```

- [ ] **Step 6: Write `pytest.ini`**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = agrispace.settings
python_files = tests/test_*.py
python_classes = Test*
python_functions = test_*
```

- [ ] **Step 7: Write `conftest.py`**

```python
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def farmer(db):
    from apps.users.models import User
    return User.objects.create_user(email='farmer@test.com', password='pass1234', role='farmer')


@pytest.fixture
def admin_user(db):
    from apps.users.models import User
    return User.objects.create_user(email='admin@test.com', password='pass1234', role='admin')


@pytest.fixture
def auth_client(api_client, farmer):
    api_client.force_authenticate(user=farmer)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client
```

- [ ] **Step 8: Create the PostgreSQL database with PostGIS**

```bash
psql -U postgres -c "CREATE USER agrispace WITH PASSWORD 'password';"
psql -U postgres -c "CREATE DATABASE agrispace OWNER agrispace;"
psql -U postgres -d agrispace -c "CREATE EXTENSION postgis;"
```

- [ ] **Step 9: Verify Django starts**

```bash
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 10: Commit**

```bash
git add backend/
git commit -m "feat: scaffold Django project with PostGIS, DRF, JWT, cors"
```

---

## Task 2: User Model + Auth

**Files:**
- Create: `backend/apps/users/models.py`
- Create: `backend/apps/users/serializers.py`
- Create: `backend/apps/users/views.py`
- Create: `backend/apps/users/urls.py`
- Create: `backend/apps/users/tests/test_auth.py`

- [ ] **Step 1: Write the failing tests**

```python
# apps/users/tests/test_auth.py
import pytest


@pytest.mark.django_db
def test_register_creates_farmer_user(api_client):
    resp = api_client.post('/api/auth/register/', {
        'email': 'new@farm.com', 'password': 'securepass1', 'farm_name': 'Green Acres'
    })
    assert resp.status_code == 201
    assert resp.data['email'] == 'new@farm.com'
    assert resp.data['role'] == 'farmer'


@pytest.mark.django_db
def test_login_sets_httponly_cookies(api_client, farmer):
    resp = api_client.post('/api/auth/login/', {
        'email': 'farmer@test.com', 'password': 'pass1234'
    })
    assert resp.status_code == 200
    assert 'access_token' in resp.cookies
    assert resp.cookies['access_token']['httponly']
    assert 'refresh_token' in resp.cookies


@pytest.mark.django_db
def test_login_wrong_password_returns_401(api_client, farmer):
    resp = api_client.post('/api/auth/login/', {
        'email': 'farmer@test.com', 'password': 'wrong'
    })
    assert resp.status_code == 401


@pytest.mark.django_db
def test_authenticated_request_without_cookie_returns_401(api_client):
    resp = api_client.get('/api/plots/')
    assert resp.status_code == 401
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest apps/users/tests/test_auth.py -v
```

Expected: 4 errors — models/views not yet defined.

- [ ] **Step 3: Write `apps/users/models.py`**

```python
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError('Email required')
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('role', 'admin')
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    farm_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=10,
        choices=[('farmer', 'Farmer'), ('admin', 'Admin')],
        default='farmer',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
```

- [ ] **Step 4: Write `apps/users/serializers.py`**

```python
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'farm_name', 'role']
        read_only_fields = ['role']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'farm_name', 'role', 'is_active', 'created_at']
        read_only_fields = fields

    created_at = serializers.DateTimeField(source='date_joined', read_only=True)
```

- [ ] **Step 5: Write `apps/users/views.py`**

```python
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class CookieTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            secure = not settings.DEBUG
            response.set_cookie('access_token', response.data['access'],
                                httponly=True, samesite='Lax', secure=secure, max_age=3600)
            response.set_cookie('refresh_token', response.data['refresh'],
                                httponly=True, samesite='Lax', secure=secure, max_age=86400 * 7)
            response.data = {'detail': 'Login successful.'}
        return response


class CookieTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from rest_framework_simplejwt.serializers import TokenRefreshSerializer
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'No refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_401_UNAUTHORIZED)
        resp = Response({'detail': 'Token refreshed.'})
        resp.set_cookie('access_token', serializer.validated_data['access'],
                        httponly=True, samesite='Lax', secure=not settings.DEBUG, max_age=3600)
        return resp
```

- [ ] **Step 6: Write `apps/users/urls.py`**

```python
from django.urls import path
from .views import RegisterView, CookieTokenObtainPairView, CookieTokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', CookieTokenObtainPairView.as_view()),
    path('refresh/', CookieTokenRefreshView.as_view()),
]
```

- [ ] **Step 7: Run migrations and tests**

```bash
python manage.py makemigrations users
python manage.py migrate
pytest apps/users/tests/test_auth.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 8: Commit**

```bash
git add apps/users/
git commit -m "feat: add custom User model with email auth and httpOnly JWT cookies"
```

---

## Task 3: Plot + CropTag Models

**Files:**
- Create: `backend/apps/plots/models.py`
- Create: `backend/apps/plots/serializers.py`
- Create: `backend/apps/plots/tests/test_models.py`

- [ ] **Step 1: Write failing model tests**

```python
# apps/plots/tests/test_models.py
import pytest
from django.contrib.gis.geos import Point, Polygon


@pytest.mark.django_db
def test_crop_tag_str(db):
    from apps.plots.models import CropTag
    tag = CropTag.objects.create(name='Maize', category='row_crop')
    assert str(tag) == 'Maize'


@pytest.mark.django_db
def test_plot_with_point_geometry_has_no_area(farmer):
    from apps.plots.models import Plot
    plot = Plot.objects.create(
        owner=farmer, name='Test Field', geometry=Point(28.0, -26.0)
    )
    assert plot.area_hectares is None


@pytest.mark.django_db
def test_plot_with_polygon_computes_area(farmer):
    from apps.plots.models import Plot
    # Small polygon ~0.5 ha
    poly = Polygon(((28.0, -26.0), (28.005, -26.0), (28.005, -26.005),
                    (28.0, -26.005), (28.0, -26.0)))
    plot = Plot.objects.create(owner=farmer, name='Poly Field', geometry=poly)
    assert plot.area_hectares is not None
    assert plot.area_hectares > 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest apps/plots/tests/test_models.py -v
```

Expected: ImportError — models not yet defined.

- [ ] **Step 3: Write `apps/plots/models.py`**

```python
import uuid
from django.contrib.gis.db import models as gis_models
from django.db import models


class CropTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20,
        choices=[('row_crop', 'Row Crop'), ('horticulture', 'Horticulture'),
                 ('orchard', 'Orchard'), ('pasture', 'Pasture'), ('other', 'Other')],
        default='other',
    )

    def __str__(self):
        return self.name


class Plot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='plots')
    name = models.CharField(max_length=255)
    geometry = gis_models.GeometryField(srid=4326)
    area_hectares = models.FloatField(null=True, blank=True)
    crop_tags = models.ManyToManyField(CropTag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.geometry and self.geometry.geom_type == 'Polygon':
            projected = self.geometry.transform(3857, clone=True)
            self.area_hectares = projected.area / 10000
        super().save(*args, **kwargs)


class WeatherCache(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    latitude = models.FloatField()
    longitude = models.FloatField()
    fetched_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    forecast_json = models.JSONField()

    class Meta:
        unique_together = ['latitude', 'longitude']


class AnalyticsSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    total_users = models.IntegerField(default=0)
    active_users_7d = models.IntegerField(default=0)
    total_plots = models.IntegerField(default=0)
    recommendations_generated = models.IntegerField(default=0)
    top_crop_tags_json = models.JSONField(default=list)
```

- [ ] **Step 4: Run migrations and model tests**

```bash
python manage.py makemigrations plots
python manage.py migrate
pytest apps/plots/tests/test_models.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Write `apps/plots/serializers.py`**

```python
from rest_framework import serializers
from django.contrib.gis.geos import GEOSGeometry
import json

from .models import Plot, CropTag


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
        except Exception as e:
            raise serializers.ValidationError(f'Invalid geometry: {e}')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['geometry'] = json.loads(instance.geometry.geojson)
        return data
```

- [ ] **Step 6: Commit**

```bash
git add apps/plots/
git commit -m "feat: add Plot, CropTag, WeatherCache, AnalyticsSnapshot models"
```

---

## Task 4: Plots CRUD API

**Files:**
- Create: `backend/apps/plots/views.py`
- Create: `backend/apps/plots/urls.py`
- Create: `backend/apps/plots/tests/test_api.py`

- [ ] **Step 1: Write failing API tests**

```python
# apps/plots/tests/test_api.py
import pytest


POINT_GEOM = {'type': 'Point', 'coordinates': [28.0, -26.0]}
POLYGON_GEOM = {
    'type': 'Polygon',
    'coordinates': [[[28.0, -26.0], [28.005, -26.0], [28.005, -26.005],
                     [28.0, -26.005], [28.0, -26.0]]]
}


@pytest.mark.django_db
def test_create_plot_with_pin(auth_client):
    resp = auth_client.post('/api/plots/', {'name': 'North Field', 'geometry': POINT_GEOM}, format='json')
    assert resp.status_code == 201
    assert resp.data['name'] == 'North Field'
    assert resp.data['geometry']['type'] == 'Point'


@pytest.mark.django_db
def test_create_plot_with_polygon_computes_area(auth_client):
    resp = auth_client.post('/api/plots/', {'name': 'Poly Field', 'geometry': POLYGON_GEOM}, format='json')
    assert resp.status_code == 201
    assert resp.data['area_hectares'] is not None


@pytest.mark.django_db
def test_list_plots_returns_only_owners_plots(auth_client, farmer, admin_user):
    from apps.plots.models import Plot
    from django.contrib.gis.geos import Point
    Plot.objects.create(owner=farmer, name='Mine', geometry=Point(28.0, -26.0))
    Plot.objects.create(owner=admin_user, name='Theirs', geometry=Point(29.0, -27.0))
    resp = auth_client.get('/api/plots/')
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]['name'] == 'Mine'


@pytest.mark.django_db
def test_delete_plot(auth_client, farmer):
    from apps.plots.models import Plot
    from django.contrib.gis.geos import Point
    plot = Plot.objects.create(owner=farmer, name='Delete Me', geometry=Point(28.0, -26.0))
    resp = auth_client.delete(f'/api/plots/{plot.id}/')
    assert resp.status_code == 204


@pytest.mark.django_db
def test_cannot_access_other_users_plot(auth_client, admin_user):
    from apps.plots.models import Plot
    from django.contrib.gis.geos import Point
    plot = Plot.objects.create(owner=admin_user, name='Admin Plot', geometry=Point(28.0, -26.0))
    resp = auth_client.get(f'/api/plots/{plot.id}/')
    assert resp.status_code == 404


@pytest.mark.django_db
def test_list_crop_tags(auth_client):
    from apps.plots.models import CropTag
    CropTag.objects.create(name='Maize', category='row_crop')
    resp = auth_client.get('/api/crop-tags/')
    assert resp.status_code == 200
    assert any(t['name'] == 'Maize' for t in resp.data)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest apps/plots/tests/test_api.py -v
```

Expected: all FAIL with 404 (routes not defined).

- [ ] **Step 3: Write `apps/plots/views.py`**

```python
from rest_framework import viewsets, generics, permissions

from .models import Plot, CropTag
from .serializers import PlotSerializer, CropTagSerializer


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
    queryset = CropTag.objects.all().order_by('name')
```

- [ ] **Step 4: Write `apps/plots/urls.py`**

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlotViewSet, CropTagListView

router = DefaultRouter()
router.register('plots', PlotViewSet, basename='plot')

urlpatterns = [
    path('', include(router.urls)),
    path('crop-tags/', CropTagListView.as_view()),
]
```

- [ ] **Step 5: Run tests**

```bash
pytest apps/plots/tests/ -v
```

Expected: all 9 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add apps/plots/
git commit -m "feat: add Plot CRUD API with ownership scoping and CropTag list"
```

---

## Task 5: Weather Client

**Files:**
- Create: `backend/apps/weather/client.py`
- Create: `backend/apps/weather/tests/test_client.py`

- [ ] **Step 1: Write failing test**

```python
# apps/weather/tests/test_client.py
import pytest
import httpx


def test_fetch_forecast_returns_daily_variables(respx_mock):
    import respx
    from apps.weather.client import fetch_forecast, DAILY_VARIABLES

    mock_response = {
        'latitude': -26.0, 'longitude': 28.0,
        'daily': {var: [0.0] * 7 for var in DAILY_VARIABLES},
        'daily_units': {var: 'mm' for var in DAILY_VARIABLES},
    }
    respx_mock.get('https://api.open-meteo.com/v1/forecast').mock(
        return_value=httpx.Response(200, json=mock_response)
    )
    result = fetch_forecast(-26.0, 28.0)
    assert 'daily' in result
    for var in DAILY_VARIABLES:
        assert var in result['daily']
```

Install `respx` for httpx mocking: `pip install respx==0.21.1` and add to requirements.txt.

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest apps/weather/tests/test_client.py -v
```

Expected: ImportError — `client.py` not yet defined.

- [ ] **Step 3: Write `apps/weather/client.py`**

```python
import httpx

OPEN_METEO_URL = 'https://api.open-meteo.com/v1/forecast'

DAILY_VARIABLES = [
    'precipitation_sum',
    'wind_speed_10m_max',
    'relative_humidity_2m_max',
    'soil_moisture_0_to_1cm',
    'temperature_2m_min',
    'temperature_2m_max',
    'et0_fao_evapotranspiration',
]


def fetch_forecast(lat: float, lng: float) -> dict:
    params = {
        'latitude': lat,
        'longitude': lng,
        'daily': ','.join(DAILY_VARIABLES),
        'forecast_days': 7,
        'timezone': 'auto',
    }
    response = httpx.get(OPEN_METEO_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
```

- [ ] **Step 4: Run test**

```bash
pytest apps/weather/tests/test_client.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/weather/
git commit -m "feat: add Open-Meteo weather client"
```

---

## Task 6: LLM Recommendation Engine

**Files:**
- Create: `backend/apps/recommendations/engine.py`
- Create: `backend/apps/recommendations/tests/test_engine.py`

- [ ] **Step 1: Write failing tests**

```python
# apps/recommendations/tests/test_engine.py
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.gis.geos import Point


MOCK_FORECAST = {
    'daily': {
        'precipitation_sum': [0.0, 0.0, 8.0, 0.0, 0.0, 0.0, 0.0],
        'wind_speed_10m_max': [12.0, 15.0, 10.0, 8.0, 9.0, 11.0, 13.0],
        'relative_humidity_2m_max': [55.0, 60.0, 75.0, 50.0, 52.0, 58.0, 61.0],
        'soil_moisture_0_to_1cm': [0.2, 0.2, 0.3, 0.3, 0.25, 0.22, 0.2],
        'temperature_2m_min': [18.0, 17.0, 15.0, 16.0, 17.0, 18.0, 19.0],
        'temperature_2m_max': [28.0, 27.0, 22.0, 25.0, 26.0, 27.0, 28.0],
        'et0_fao_evapotranspiration': [4.5, 4.2, 3.0, 3.8, 4.0, 4.3, 4.5],
    }
}

MOCK_LLM_CARDS = [
    {'activity': 'spray', 'status': 'green', 'title': 'Good spraying conditions', 'reason': 'Low wind and no rain forecast today.'},
    {'activity': 'irrigate', 'status': 'amber', 'title': 'Caution: rain Wednesday', 'reason': 'Hold irrigation — 8mm rain expected in 48 hours.'},
    {'activity': 'plant', 'status': 'green', 'title': 'Good planting window', 'reason': 'Warm temperatures and adequate soil moisture.'},
    {'activity': 'harvest', 'status': 'green', 'title': 'Good harvest conditions', 'reason': 'Low humidity and dry conditions today.'},
]


@pytest.mark.django_db
def test_get_recommendations_returns_four_cards(farmer, mocker):
    from apps.recommendations.engine import get_recommendations
    from apps.plots.models import Plot

    plot = Plot.objects.create(owner=farmer, name='Test', geometry=Point(28.0, -26.0))
    mocker.patch('apps.recommendations.engine.fetch_forecast', return_value=MOCK_FORECAST)
    mocker.patch('apps.recommendations.engine._call_llm', return_value=MOCK_LLM_CARDS)

    cards = get_recommendations(plot)
    assert len(cards) == 4
    activities = {c['activity'] for c in cards}
    assert activities == {'spray', 'irrigate', 'plant', 'harvest'}


@pytest.mark.django_db
def test_get_recommendations_uses_weather_cache(farmer, mocker):
    from apps.recommendations.engine import get_recommendations
    from apps.plots.models import Plot, WeatherCache
    from django.utils import timezone
    from datetime import timedelta

    plot = Plot.objects.create(owner=farmer, name='Cached', geometry=Point(28.0, -26.0))
    cached_forecast = {**MOCK_FORECAST, 'recommendations': MOCK_LLM_CARDS,
                       'reco_date': timezone.now().date().isoformat()}
    WeatherCache.objects.create(latitude=-26.0, longitude=28.0,
                                forecast_json=cached_forecast,
                                expires_at=timezone.now() + timedelta(hours=1))

    fetch_mock = mocker.patch('apps.recommendations.engine.fetch_forecast')
    llm_mock = mocker.patch('apps.recommendations.engine._call_llm')

    cards = get_recommendations(plot)
    fetch_mock.assert_not_called()
    llm_mock.assert_not_called()
    assert len(cards) == 4


@pytest.mark.django_db
def test_fallback_used_when_llm_fails(farmer, mocker):
    from apps.recommendations.engine import get_recommendations
    from apps.plots.models import Plot

    plot = Plot.objects.create(owner=farmer, name='Fallback', geometry=Point(28.0, -26.0))
    mocker.patch('apps.recommendations.engine.fetch_forecast', return_value=MOCK_FORECAST)
    mocker.patch('apps.recommendations.engine._call_llm', side_effect=Exception('API down'))

    cards = get_recommendations(plot)
    assert len(cards) == 4
    for card in cards:
        assert card['status'] in ('green', 'amber', 'red')
        assert 'title' in card and 'reason' in card
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest apps/recommendations/tests/test_engine.py -v
```

Expected: ImportError.

- [ ] **Step 3: Write `apps/recommendations/engine.py`**

```python
import json
import anthropic
from datetime import timedelta

from django.utils import timezone

from apps.plots.models import Plot, WeatherCache
from apps.weather.client import fetch_forecast

TOOL_SCHEMA = {
    'name': 'submit_recommendations',
    'description': 'Submit agricultural activity recommendations based on weather forecast.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'recommendations': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'activity': {'type': 'string', 'enum': ['spray', 'irrigate', 'plant', 'harvest']},
                        'status': {'type': 'string', 'enum': ['green', 'amber', 'red']},
                        'title': {'type': 'string', 'maxLength': 80},
                        'reason': {'type': 'string', 'maxLength': 200},
                    },
                    'required': ['activity', 'status', 'title', 'reason'],
                },
                'minItems': 4,
                'maxItems': 4,
            }
        },
        'required': ['recommendations'],
    },
}

SYSTEM_PROMPT = (
    'You are an expert agronomist. Analyze the 7-day weather forecast and provide one '
    'recommendation card for each of the 4 activities: spray, irrigate, plant, harvest. '
    'status: green=good conditions, amber=caution/wait, red=do not proceed. '
    'title: max 10 words, action-oriented. reason: one clear sentence citing the key weather factor. '
    'Consider the hemisphere for seasonal context.'
)


def get_recommendations(plot: Plot) -> list[dict]:
    if plot.geometry.geom_type == 'Point':
        lat = round(plot.geometry.y, 2)
        lng = round(plot.geometry.x, 2)
    else:
        centroid = plot.geometry.centroid
        lat = round(centroid.y, 2)
        lng = round(centroid.x, 2)

    today = timezone.now().date().isoformat()

    cached = WeatherCache.objects.filter(
        latitude=lat, longitude=lng, expires_at__gt=timezone.now()
    ).first()

    if cached:
        data = cached.forecast_json
        if data.get('reco_date') == today and 'recommendations' in data:
            return data['recommendations']
        forecast = data
    else:
        forecast = fetch_forecast(lat, lng)
        cached, _ = WeatherCache.objects.update_or_create(
            latitude=lat, longitude=lng,
            defaults={'forecast_json': forecast, 'expires_at': timezone.now() + timedelta(hours=1)},
        )

    crop_names = list(plot.crop_tags.values_list('name', flat=True))
    hemisphere = 'northern' if lat >= 0 else 'southern'

    try:
        cards = _call_llm(forecast, crop_names, hemisphere)
    except Exception:
        cards = _fallback_recommendations(forecast)

    cached.forecast_json = {**forecast, 'recommendations': cards, 'reco_date': today}
    cached.save(update_fields=['forecast_json'])
    return cards


def _call_llm(forecast: dict, crop_tags: list[str], hemisphere: str) -> list[dict]:
    client = anthropic.Anthropic()
    user_message = (
        f"Crops: {', '.join(crop_tags) if crop_tags else 'General'}\n"
        f"Hemisphere: {hemisphere}\nDate: {timezone.now().date().isoformat()}\n\n"
        f"Forecast:\n{json.dumps(forecast.get('daily', {}), indent=2)}"
    )
    response = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=[TOOL_SCHEMA],
        tool_choice={'type': 'tool', 'name': 'submit_recommendations'},
        messages=[{'role': 'user', 'content': user_message}],
    )
    for block in response.content:
        if block.type == 'tool_use' and block.name == 'submit_recommendations':
            return block.input['recommendations']
    raise ValueError('LLM did not call submit_recommendations')


def _fallback_recommendations(forecast: dict) -> list[dict]:
    daily = forecast.get('daily', {})
    precip = daily.get('precipitation_sum', [0] * 7)
    wind = daily.get('wind_speed_10m_max', [0] * 7)
    humidity = daily.get('relative_humidity_2m_max', [50] * 7)
    temp_min = daily.get('temperature_2m_min', [15] * 7)

    today_rain = precip[0] if precip else 0
    today_wind = wind[0] if wind else 0
    today_humidity = humidity[0] if humidity else 50
    tomorrow_rain = precip[1] if len(precip) > 1 else 0

    return [
        {
            'activity': 'spray',
            'status': 'red' if today_wind > 20 or today_rain > 0 else 'amber' if tomorrow_rain > 5 else 'green',
            'title': 'Check local conditions before spraying',
            'reason': 'Live weather data temporarily unavailable — verify wind and rain locally.',
        },
        {
            'activity': 'irrigate',
            'status': 'red' if today_rain > 10 else 'amber' if today_rain > 2 else 'green',
            'title': 'Check soil moisture before irrigating',
            'reason': 'Live weather data temporarily unavailable — check soil moisture manually.',
        },
        {
            'activity': 'plant',
            'status': 'red' if temp_min[0] < 2 else 'amber' if today_rain > 5 else 'green',
            'title': 'Check temperature before planting',
            'reason': 'Live weather data temporarily unavailable — verify frost risk locally.',
        },
        {
            'activity': 'harvest',
            'status': 'red' if today_rain > 0 or today_humidity > 85 else 'amber' if today_humidity > 70 else 'green',
            'title': 'Check humidity before harvesting',
            'reason': 'Live weather data temporarily unavailable — check humidity locally.',
        },
    ]
```

- [ ] **Step 4: Run tests**

```bash
pytest apps/recommendations/tests/test_engine.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/recommendations/
git commit -m "feat: add LLM recommendation engine with weather cache and rule-based fallback"
```

---

## Task 7: Recommendations API Endpoint

**Files:**
- Create: `backend/apps/recommendations/views.py`
- Create: `backend/apps/recommendations/urls.py`
- Create: `backend/apps/recommendations/tests/test_api.py`

- [ ] **Step 1: Write failing API test**

```python
# apps/recommendations/tests/test_api.py
import pytest
from django.contrib.gis.geos import Point


MOCK_CARDS = [
    {'activity': 'spray', 'status': 'green', 'title': 'Good spray day', 'reason': 'Low wind.'},
    {'activity': 'irrigate', 'status': 'amber', 'title': 'Hold irrigation', 'reason': 'Rain coming.'},
    {'activity': 'plant', 'status': 'green', 'title': 'Good planting', 'reason': 'Warm and dry.'},
    {'activity': 'harvest', 'status': 'red', 'title': 'Avoid harvesting', 'reason': 'High humidity.'},
]


@pytest.mark.django_db
def test_recommendations_endpoint_returns_cards(auth_client, farmer, mocker):
    from apps.plots.models import Plot
    plot = Plot.objects.create(owner=farmer, name='Test', geometry=Point(28.0, -26.0))
    mocker.patch('apps.recommendations.views.get_recommendations', return_value=MOCK_CARDS)
    resp = auth_client.get(f'/api/plots/{plot.id}/recommendations/')
    assert resp.status_code == 200
    assert len(resp.data) == 4
    assert resp.data[0]['activity'] == 'spray'


@pytest.mark.django_db
def test_recommendations_endpoint_rejects_other_users_plot(auth_client, admin_user):
    from apps.plots.models import Plot
    plot = Plot.objects.create(owner=admin_user, name='Admin Plot', geometry=Point(28.0, -26.0))
    resp = auth_client.get(f'/api/plots/{plot.id}/recommendations/')
    assert resp.status_code == 404
```

- [ ] **Step 2: Run to verify failures**

```bash
pytest apps/recommendations/tests/test_api.py -v
```

Expected: 2 FAIL with 404.

- [ ] **Step 3: Write `apps/recommendations/views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404

from apps.plots.models import Plot
from .engine import get_recommendations


class RecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, plot_id):
        plot = get_object_or_404(Plot, id=plot_id, owner=request.user)
        cards = get_recommendations(plot)
        return Response(cards)
```

- [ ] **Step 4: Write `apps/recommendations/urls.py`**

```python
from django.urls import path
from .views import RecommendationsView

urlpatterns = [
    path('plots/<uuid:plot_id>/recommendations/', RecommendationsView.as_view()),
]
```

- [ ] **Step 5: Run tests**

```bash
pytest apps/recommendations/tests/test_api.py -v
```

Expected: 2 PASS.

- [ ] **Step 6: Commit**

```bash
git add apps/recommendations/
git commit -m "feat: add recommendations API endpoint"
```

---

## Task 8: Admin API + Analytics

**Files:**
- Create: `backend/apps/admin_panel/serializers.py`
- Create: `backend/apps/admin_panel/views.py`
- Create: `backend/apps/admin_panel/urls.py`
- Create: `backend/apps/plots/management/commands/snapshot_analytics.py`
- Create: `backend/apps/admin_panel/tests/test_api.py`

- [ ] **Step 1: Write failing tests**

```python
# apps/admin_panel/tests/test_api.py
import pytest


@pytest.mark.django_db
def test_farmer_cannot_access_admin_users(auth_client):
    resp = auth_client.get('/api/admin/users/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_admin_can_list_users(admin_client, farmer):
    resp = admin_client.get('/api/admin/users/')
    assert resp.status_code == 200
    emails = [u['email'] for u in resp.data]
    assert 'farmer@test.com' in emails


@pytest.mark.django_db
def test_admin_can_deactivate_user(admin_client, farmer):
    resp = admin_client.patch(f'/api/admin/users/{farmer.id}/', {'is_active': False}, format='json')
    assert resp.status_code == 200
    farmer.refresh_from_db()
    assert not farmer.is_active


@pytest.mark.django_db
def test_admin_analytics_returns_snapshot(admin_client):
    from apps.plots.models import AnalyticsSnapshot
    from datetime import date
    AnalyticsSnapshot.objects.create(date=date.today(), total_users=5, active_users_7d=3,
                                     total_plots=10, recommendations_generated=20)
    resp = admin_client.get('/api/admin/analytics/')
    assert resp.status_code == 200
    assert len(resp.data) >= 1
    assert resp.data[0]['total_users'] == 5
```

- [ ] **Step 2: Run to verify failures**

```bash
pytest apps/admin_panel/tests/test_api.py -v
```

Expected: 4 FAIL.

- [ ] **Step 3: Write `apps/admin_panel/serializers.py`**

```python
from rest_framework import serializers
from apps.users.models import User
from apps.plots.models import AnalyticsSnapshot


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'farm_name', 'role', 'is_active', 'date_joined']
        read_only_fields = ['id', 'email', 'farm_name', 'role', 'date_joined']


class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSnapshot
        fields = '__all__'
```

- [ ] **Step 4: Write `apps/admin_panel/views.py`**

```python
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from apps.users.models import User
from apps.plots.models import AnalyticsSnapshot
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
```

- [ ] **Step 5: Write `apps/admin_panel/urls.py`**

```python
from django.urls import path
from .views import AdminUserListView, AdminUserDetailView, AdminAnalyticsView

urlpatterns = [
    path('users/', AdminUserListView.as_view()),
    path('users/<uuid:pk>/', AdminUserDetailView.as_view()),
    path('analytics/', AdminAnalyticsView.as_view()),
]
```

- [ ] **Step 6: Write the analytics management command**

```python
# apps/plots/management/commands/snapshot_analytics.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta

from apps.users.models import User
from apps.plots.models import Plot, CropTag, AnalyticsSnapshot, WeatherCache


class Command(BaseCommand):
    help = 'Create a daily analytics snapshot'

    def handle(self, *args, **options):
        today = timezone.now().date()
        week_ago = timezone.now() - timedelta(days=7)

        top_tags = (
            CropTag.objects.annotate(plot_count=Count('plot'))
            .order_by('-plot_count')[:10]
            .values('name', 'plot_count')
        )

        reco_count = WeatherCache.objects.filter(
            fetched_at__date=today,
            forecast_json__reco_date=today.isoformat(),
        ).count()

        snapshot, created = AnalyticsSnapshot.objects.update_or_create(
            date=today,
            defaults={
                'total_users': User.objects.count(),
                'active_users_7d': User.objects.filter(last_login__gte=week_ago).count(),
                'total_plots': Plot.objects.count(),
                'recommendations_generated': reco_count,
                'top_crop_tags_json': list(top_tags),
            },
        )
        self.stdout.write(self.style.SUCCESS(f'Snapshot {"created" if created else "updated"} for {today}'))
```

- [ ] **Step 7: Run all tests**

```bash
pytest apps/admin_panel/tests/test_api.py -v
```

Expected: 4 PASS.

- [ ] **Step 8: Run full test suite**

```bash
pytest -v
```

Expected: all tests PASS.

- [ ] **Step 9: Commit**

```bash
git add apps/admin_panel/ apps/plots/management/
git commit -m "feat: add admin user management, analytics API, and snapshot management command"
```

---

## Task 9: Seed Data + Smoke Test

**Files:**
- Create: `backend/seed.py`

- [ ] **Step 1: Write `seed.py`**

```python
# Run with: python seed.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrispace.settings')
django.setup()

from apps.users.models import User
from apps.plots.models import CropTag, Plot
from django.contrib.gis.geos import Point

# Crop tags
tags = [
    ('Maize', 'row_crop'), ('Wheat', 'row_crop'), ('Soybeans', 'row_crop'),
    ('Tomatoes', 'horticulture'), ('Peppers', 'horticulture'), ('Potatoes', 'horticulture'),
    ('Apples', 'orchard'), ('Citrus', 'orchard'),
    ('Grass', 'pasture'), ('Alfalfa', 'pasture'),
]
for name, cat in tags:
    CropTag.objects.get_or_create(name=name, defaults={'category': cat})

# Admin user
admin = User.objects.filter(email='admin@agrispace.com').first()
if not admin:
    User.objects.create_user(email='admin@agrispace.com', password='admin1234', role='admin', farm_name='Admin')
    print('Admin created: admin@agrispace.com / admin1234')

# Demo farmer
farmer = User.objects.filter(email='farmer@demo.com').first()
if not farmer:
    farmer = User.objects.create_user(email='farmer@demo.com', password='farmer1234', farm_name='Green Acres')
    Plot.objects.create(owner=farmer, name='North Field', geometry=Point(28.05, -26.1))
    print('Farmer created: farmer@demo.com / farmer1234')

print('Seed complete.')
```

- [ ] **Step 2: Run seed**

```bash
python seed.py
```

Expected output:
```
Admin created: admin@agrispace.com / admin1234
Farmer created: farmer@demo.com / farmer1234
Seed complete.
```

- [ ] **Step 3: Start the dev server and smoke-test key endpoints**

```bash
python manage.py runserver
```

In a separate terminal:
```bash
# Login
curl -c cookies.txt -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"farmer@demo.com","password":"farmer1234"}'
# Expected: {"detail": "Login successful."}

# List plots (authenticated via cookie)
curl -b cookies.txt http://localhost:8000/api/plots/
# Expected: JSON array with North Field

# Get recommendations (will call Open-Meteo + Claude)
PLOT_ID=$(curl -b cookies.txt http://localhost:8000/api/plots/ | python -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")
curl -b cookies.txt http://localhost:8000/api/plots/$PLOT_ID/recommendations/
# Expected: JSON array of 4 recommendation cards
```

- [ ] **Step 4: Commit**

```bash
git add seed.py
git commit -m "chore: add seed data script with demo farmer, admin, and crop tags"
```

---

## Backend Complete

The Django API is now fully functional. Proceed to the frontend plan:
`docs/superpowers/plans/2026-05-14-agri-space-frontend.md`
