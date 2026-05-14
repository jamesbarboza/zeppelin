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
