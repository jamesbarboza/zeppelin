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
