"""
Integration tests — end-to-end flows and template rendering.
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


# ── 18.1 End-to-end flow tests ────────────────────────────────────────────────

def test_dashboard_loads_all_three_sections(client):
    resp = client.get('/')
    soup = BeautifulSoup(resp.data, 'html.parser')
    headers = [h.get_text(strip=True) for h in soup.select('.section-header')]
    assert any('Appointment' in h for h in headers), "Appointments section missing"
    assert any('Guideline' in h or 'Health' in h for h in headers), "Guidelines section missing"
    assert any('Provider' in h for h in headers), "Providers section missing"


def test_submit_age_range_shows_recommendations(client):
    resp = client.post('/', data={'age_range': '18-30'})
    soup = BeautifulSoup(resp.data, 'html.parser')
    items = soup.select('.recommendations-list li')
    assert len(items) == len(health_guidelines['18-30'])


def test_submit_different_age_range_updates_recommendations(client):
    resp1 = client.post('/', data={'age_range': '18-30'})
    resp2 = client.post('/', data={'age_range': '51+'})
    html1 = resp1.data.decode()
    html2 = resp2.data.decode()
    # Each response should contain its own guidelines, not the other's
    assert health_guidelines['18-30'][0] in html1
    assert health_guidelines['51+'][0] in html2
    assert health_guidelines['51+'][0] not in html1
    assert health_guidelines['18-30'][0] not in html2


def test_submit_invalid_age_range_graceful(client):
    resp = client.post('/', data={'age_range': 'invalid'})
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.data, 'html.parser')
    # Page still renders all sections
    assert len(soup.select('.section')) >= 3
    # No recommendations shown
    assert len(soup.select('.recommendations-list li')) == 0


# ── 18.2 Template integration tests ──────────────────────────────────────────

def test_jinja2_appointment_loop_renders_all(client):
    resp = client.get('/')
    soup = BeautifulSoup(resp.data, 'html.parser')
    items = soup.select('.appointment-item')
    assert len(items) == len(app_module.appointments)


def test_jinja2_provider_loop_renders_all(client):
    resp = client.get('/')
    soup = BeautifulSoup(resp.data, 'html.parser')
    items = soup.select('.provider-item')
    assert len(items) == len(app_module.providers)


def test_conditional_recommendations_hidden_on_get(client):
    resp = client.get('/')
    soup = BeautifulSoup(resp.data, 'html.parser')
    assert soup.find(class_='recommendations') is None


def test_conditional_recommendations_shown_on_post(client):
    resp = client.post('/', data={'age_range': '31-50'})
    soup = BeautifulSoup(resp.data, 'html.parser')
    assert soup.find(class_='recommendations') is not None


def test_variable_interpolation_appointment_fields(client):
    resp = client.get('/')
    html = resp.data.decode()
    for appt in app_module.appointments:
        assert appt['date'] in html
        assert appt['time'] in html
        assert appt['hospital'] in html
        assert appt['purpose'] in html


def test_form_state_persistence_after_post(client):
    """The dropdown should show the submitted age range as selected."""
    for age in health_guidelines.keys():
        resp = client.post('/', data={'age_range': age})
        soup = BeautifulSoup(resp.data, 'html.parser')
        selected = soup.find('option', selected=True)
        assert selected is not None
        assert selected.get('value') == age, f"Expected '{age}' selected, got '{selected.get('value')}'"
