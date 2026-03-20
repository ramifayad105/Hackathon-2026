"""
Unit tests for the Flask preventive care dashboard.
"""
import pytest
from bs4 import BeautifulSoup
import app as app_module
from app import app as flask_app, health_guidelines


@pytest.fixture(autouse=True)
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c


# ── 17.1 Appointment display ──────────────────────────────────────────────────

def test_zero_appointments_shows_empty_message(client):
    orig = app_module.appointments[:]
    app_module.appointments.clear()
    try:
        resp = client.get('/')
        assert b'No upcoming appointments' in resp.data
    finally:
        app_module.appointments[:] = orig


def test_single_appointment_renders(client):
    appt = {'date': 'June 1, 2026', 'time': '10:00 AM', 'hospital': 'Test Hospital', 'purpose': 'Checkup'}
    orig = app_module.appointments[:]
    app_module.appointments[:] = [appt]
    try:
        resp = client.get('/')
        html = resp.data.decode()
        assert 'Test Hospital' in html
        assert 'Checkup' in html
    finally:
        app_module.appointments[:] = orig


def test_multiple_appointments_all_render(client):
    appts = [
        {'date': 'June 1, 2026', 'time': '9:00 AM', 'hospital': 'Alpha Clinic', 'purpose': 'Exam A'},
        {'date': 'June 2, 2026', 'time': '2:00 PM', 'hospital': 'Beta Hospital', 'purpose': 'Exam B'},
    ]
    orig = app_module.appointments[:]
    app_module.appointments[:] = appts
    try:
        resp = client.get('/')
        html = resp.data.decode()
        assert 'Alpha Clinic' in html
        assert 'Beta Hospital' in html
    finally:
        app_module.appointments[:] = orig


# ── 17.2 Age range selection ──────────────────────────────────────────────────

def test_get_request_no_recommendations(client):
    resp = client.get('/')
    soup = BeautifulSoup(resp.data, 'html.parser')
    assert len(soup.select('.recommendations-list li')) == 0


def test_post_18_30_returns_correct_guidelines(client):
    resp = client.post('/', data={'age_range': '18-30'})
    html = resp.data.decode()
    for item in health_guidelines['18-30']:
        assert item in html


def test_post_31_50_returns_correct_guidelines(client):
    resp = client.post('/', data={'age_range': '31-50'})
    html = resp.data.decode()
    for item in health_guidelines['31-50']:
        assert item in html


def test_post_51_plus_returns_correct_guidelines(client):
    resp = client.post('/', data={'age_range': '51+'})
    html = resp.data.decode()
    for item in health_guidelines['51+']:
        assert item in html


def test_post_invalid_age_range_returns_empty(client):
    resp = client.post('/', data={'age_range': '99-100'})
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.data, 'html.parser')
    assert len(soup.select('.recommendations-list li')) == 0


def test_post_missing_form_data_returns_empty(client):
    resp = client.post('/', data={})
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.data, 'html.parser')
    assert len(soup.select('.recommendations-list li')) == 0


# ── 17.3 Provider display ─────────────────────────────────────────────────────

def test_at_least_three_providers_render(client):
    resp = client.get('/')
    soup = BeautifulSoup(resp.data, 'html.parser')
    assert len(soup.select('.provider-item')) >= 3


def test_provider_name_and_specializations_render(client):
    resp = client.get('/')
    html = resp.data.decode()
    for prov in app_module.providers:
        assert prov['name'] in html
        for spec in prov['specializations']:
            assert spec in html


# ── 17.4 HTTP methods ─────────────────────────────────────────────────────────

def test_get_root_returns_200(client):
    assert client.get('/').status_code == 200


def test_post_root_returns_200(client):
    assert client.post('/', data={'age_range': '18-30'}).status_code == 200


def test_invalid_route_returns_404(client):
    assert client.get('/nonexistent').status_code == 404
