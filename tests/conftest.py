"""Shared pytest fixtures."""
import pytest
import sys
import os

# Ensure the project root is on the path so `app` can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app as flask_app, health_guidelines, appointments, providers


@pytest.fixture()
def app():
    flask_app.config.update({'TESTING': True})
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def guidelines():
    return health_guidelines


@pytest.fixture()
def sample_appointments():
    return appointments


@pytest.fixture()
def sample_providers():
    return providers
