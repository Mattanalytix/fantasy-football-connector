import requests
from unittest.mock import patch, MagicMock
import pytest

from fetch.bootstrap_static import (
    BootstrapStaticFetcher,
    fetch_bootstrap_static
)


@pytest.fixture
def sample_bootstrap_data():
    """Sample data for testing."""
    return {
        "elements": [{"id": 1, "name": "test1"}],
        "teams": [{"id": 2, "name": "test2"}],
        "events": [{"id": 3, "name": "test3"}],
        "element_types": [{"id": 4, "name": "test4"}]
    }


@patch("fetch.bootstrap_static.requests.get")
def test_fetch_success(mock_get, sample_bootstrap_data):
    """Test successful fetch from the API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_bootstrap_data
    mock_get.return_value = mock_response

    fetcher = BootstrapStaticFetcher()
    data = fetcher.run()

    assert data == sample_bootstrap_data
    mock_get.assert_called_once_with(fetcher.URL)
    assert isinstance(data, dict)
    assert "elements" in data
    assert "teams" in data
    assert "events" in data
    assert "element_types" in data


@patch("fetch.bootstrap_static.requests.get")
def test_fetch_503_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_response.raise_for_status.side_effect = \
        requests.exceptions.HTTPError()
    mock_get.return_value = mock_response

    fetcher = BootstrapStaticFetcher()

    with pytest.raises(requests.exceptions.HTTPError):
        fetcher.run()


@patch("fetch.bootstrap_static.requests.get")
def test_fetch_503_error_logs_message(mock_get, caplog):
    # Mock the 503 response
    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_response.raise_for_status.side_effect = \
        requests.exceptions.HTTPError()
    mock_get.return_value = mock_response

    fetcher = BootstrapStaticFetcher()

    with pytest.raises(requests.exceptions.HTTPError):
        with caplog.at_level("ERROR"):  # Capture ERROR logs
            fetcher.run()

    # Now assert the log message
    assert "Service Unavailable (503) - The game may be updating." \
        in caplog.text


@patch("fetch.bootstrap_static.__fetch_bootstrap_static_internal")
def test_fetch_bootstrap_static(mock_internal_fetch):
    mock_internal_fetch.return_value = {"dummy": "data"}

    result = fetch_bootstrap_static()
    assert result == {"dummy": "data"}

    fetch_bootstrap_static(force_refresh=True)
    mock_internal_fetch.cache_clear.assert_called_once()
