"""
Pytest configuration and shared fixtures for API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture: FastAPI TestClient for making test requests.
    
    Provides a test client connected to the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture: Reset activities state before and after each test.
    
    Since the activities dictionary is stored in-memory, we need to reset it
    to ensure test isolation. This fixture resets the participants list for
    each activity to its original state before the test runs.
    """
    # Store original state
    original_state = {
        name: {**details, "participants": details["participants"].copy()}
        for name, details in activities.items()
    }
    
    yield  # Test runs here
    
    # Restore original state after test
    for name, details in original_state.items():
        activities[name]["participants"] = details["participants"].copy()


@pytest.fixture
def sample_activity_name():
    """Fixture: A sample activity name for testing."""
    return "Chess Club"


@pytest.fixture
def sample_email():
    """Fixture: A sample email for testing."""
    return "test.student@mergington.edu"
