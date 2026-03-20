"""
Property-based tests using Hypothesis.
Properties 1-10 as defined in the spec.
"""
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from bs4 import BeautifulSoup

from app import app as flask_app, health_guidelines

VALID_AGE_RANGES = list(health_guidelines.keys())  # ['18-30', '31-50', '51+']

# ── Strategies ────────────────────────────────────────────────────────────────

appt_strategy = st.fixed_dictionaries({
    'date':     st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), whitelist_characters=',/')),
    'time':     st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), whitelist_characters=':')),
    'hospital': st.text(min_size=1, max_size=60, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
    'purpose':  st.text(min_size=1, max_size=60, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
})

provider_strategy = st.fixed_dictionaries({
    'name':            st.text(min_size=1, max_size=60, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
    'specializations': st.lists(
        st.text(min_size=1, max_size=40, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
        min_size=1, max_size=5,
    ),
})


def _render(client, appts=None, provs=None, age=None):
    """Helper: render the dashboard via the test client with injected data."""
    with flask_app.test_request_context():
        from flask import template_rendered
        from contextlib import contextmanager

    if age:
        resp = client.post('/', data={'age_range': age})
    else:
        resp = client.get('/')
    return resp


def _get_html(client, appts, provs, age=None):
    """Render home.html with arbitrary data by patching app-level lists."""
    import app as app_module
    orig_appts = app_module.appointments[:]
    orig_provs = app_module.providers[:]
    app_module.appointments[:] = appts
    app_module.providers[:] = provs
    try:
        if age:
            resp = client.post('/', data={'age_range': age})
        else:
            resp = client.get('/')
        return resp.data.decode('utf-8')
    finally:
        app_module.appointments[:] = orig_appts
        app_module.providers[:] = orig_provs


@pytest.fixture()
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c


# ── Property 1: Appointment List Display ─────────────────────────────────────

@given(appts=st.lists(appt_strategy, min_size=1, max_size=10))
@settings(max_examples=30)
def test_property1_appointment_list_display(appts):
    """All appointments in the data list appear in the rendered HTML."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        html = _get_html(client, appts, [], age=None)
    for appt in appts:
        assert appt['hospital'].strip() in html, f"Hospital '{appt['hospital']}' missing from HTML"


# ── Property 2: Complete Appointment Information Rendering ────────────────────

@given(appt=appt_strategy)
@settings(max_examples=30)
def test_property2_complete_appointment_info(appt):
    """Every field of an appointment (date, time, hospital, purpose) appears in HTML."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        html = _get_html(client, [appt], [], age=None)
    for field in ('date', 'time', 'hospital', 'purpose'):
        assert appt[field].strip() in html, f"Field '{field}' value missing from HTML"


# ── Property 3: Age Range Guidelines Mapping ─────────────────────────────────

@given(age_range=st.sampled_from(VALID_AGE_RANGES))
def test_property3_age_range_guidelines_mapping(age_range):
    """Each valid age range returns the correct set of guidelines."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        resp = client.post('/', data={'age_range': age_range})
    html = resp.data.decode('utf-8')
    for test in health_guidelines[age_range]:
        assert test in html, f"Guideline '{test}' missing for age range '{age_range}'"


# ── Property 4: Individual Test Item Rendering ────────────────────────────────

@given(tests=st.lists(
    st.text(min_size=1, max_size=40, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
    min_size=1, max_size=8, unique=True,
))
@settings(max_examples=30)
def test_property4_individual_test_item_rendering(tests):
    """Each recommended test item appears as a separate entry in the HTML."""
    import app as app_module
    orig = dict(app_module.health_guidelines)
    app_module.health_guidelines['18-30'] = tests
    flask_app.config['TESTING'] = True
    try:
        with flask_app.test_client() as client:
            resp = client.post('/', data={'age_range': '18-30'})
        html = resp.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        items = [li.get_text(strip=True) for li in soup.select('.recommendations-list li')]
        for test in tests:
            assert any(test.strip() in item for item in items), f"Test item '{test}' not individually rendered"
    finally:
        app_module.health_guidelines['18-30'] = orig['18-30']


# ── Property 5: Provider List Display ────────────────────────────────────────

@given(provs=st.lists(provider_strategy, min_size=1, max_size=8))
@settings(max_examples=30)
def test_property5_provider_list_display(provs):
    """All providers in the data list appear in the rendered HTML."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        html = _get_html(client, [], provs, age=None)
    for prov in provs:
        assert prov['name'].strip() in html, f"Provider '{prov['name']}' missing from HTML"


# ── Property 6: Complete Provider Information Rendering ──────────────────────

@given(prov=provider_strategy)
@settings(max_examples=30)
def test_property6_complete_provider_info(prov):
    """Provider name and all specializations appear in the rendered HTML."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        html = _get_html(client, [], [prov], age=None)
    assert prov['name'].strip() in html
    for spec in prov['specializations']:
        assert spec.strip() in html, f"Specialization '{spec}' missing from HTML"


# ── Property 7: Form Data Extraction ─────────────────────────────────────────

@given(age_range=st.sampled_from(VALID_AGE_RANGES))
def test_property7_form_data_extraction(age_range):
    """POSTing a valid age_range value results in that value being reflected in the response."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        resp = client.post('/', data={'age_range': age_range})
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    # The selected age range should appear somewhere in the rendered page
    assert age_range in html


# ── Property 8: Selected Age Range Persistence ───────────────────────────────

@given(age_range=st.sampled_from(VALID_AGE_RANGES))
def test_property8_selected_age_range_persistence(age_range):
    """After POSTing an age range, the dropdown shows that option as selected."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        resp = client.post('/', data={'age_range': age_range})
    soup = BeautifulSoup(resp.data, 'html.parser')
    selected_option = soup.find('option', {'selected': True, 'value': age_range})
    assert selected_option is not None, f"Option '{age_range}' not marked as selected in dropdown"


# ── Property 9: Invalid Age Range Handling ───────────────────────────────────

@given(age_range=st.text(min_size=1).filter(lambda x: x not in VALID_AGE_RANGES))
@settings(max_examples=30)
def test_property9_invalid_age_range_handling(age_range):
    """Invalid age ranges produce an empty recommendations list (no crash)."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        resp = client.post('/', data={'age_range': age_range})
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.data, 'html.parser')
    recs = soup.select('.recommendations-list li')
    assert len(recs) == 0, f"Expected no recommendations for invalid range '{age_range}', got {len(recs)}"


# ── Property 10: Request-Scoped State Management ─────────────────────────────

@given(age_range=st.sampled_from(VALID_AGE_RANGES))
def test_property10_request_scoped_state(age_range):
    """Each request is independent — state from one POST doesn't bleed into a GET."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        # POST sets recommendations
        post_resp = client.post('/', data={'age_range': age_range})
        assert age_range in post_resp.data.decode('utf-8')
        # Subsequent GET should have no recommendations
        get_resp = client.get('/')
    soup = BeautifulSoup(get_resp.data, 'html.parser')
    recs = soup.select('.recommendations-list li')
    assert len(recs) == 0, "GET request should not carry over recommendations from previous POST"
