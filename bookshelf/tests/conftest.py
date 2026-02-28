# -*- coding: utf-8 -*-
"""Pytest fixtures for integration tests."""

import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from models import db as _db


@pytest.fixture(scope='function')
def app():
    """Create a fresh app instance for each test."""
    app = create_app(testing=True)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Database session for direct DB operations in tests."""
    with app.app_context():
        yield _db.session
