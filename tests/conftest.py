import pytest


@pytest.fixture
def sample_bootstrap_data():
    """Sample data for testing."""
    return {
        "elements": [{"id": 1, "name": "test1"}],
        "teams": [{"id": 2, "name": "test2"}],
        "events": [{"id": 3, "name": "test3"}],
        "element_types": [{"id": 4, "name": "test4"}]
    }


@pytest.fixture
def element_summary_data():
    """
    Fixture providing sample element summary data with fixtures, history, and
    history_past.
    """
    return {
        "fixtures": [{"fixture_data": "example"}],
        "history": [{"history_data": "example"}],
        "history_past": [{"past_data": "example"}]
    }
