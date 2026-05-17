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
