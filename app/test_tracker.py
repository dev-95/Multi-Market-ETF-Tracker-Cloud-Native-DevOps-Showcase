import json
import pytest
import tracker as tracker_module
from tracker import app


def _mock_fetch(fail_ticker=None):
    """Returns a fetch_ticker side-effect that fails for one symbol."""
    def _fetch(symbol):
        if symbol == fail_ticker:
            raise ConnectionError("simulated network failure")
        return {"ticker": symbol, "price": 100.00, "change_pct": 1.50}
    return _fetch


@pytest.fixture
def client(mocker):
    mocker.patch("tracker.fetch_ticker", side_effect=_mock_fetch())
    with app.test_client() as c:
        yield c


# --- / ---

def test_market_summary_returns_200(client):
    assert client.get("/").status_code == 200


def test_market_summary_returns_json_array(client):
    data = json.loads(client.get("/").data)
    assert isinstance(data, list)
    assert len(data) == len(tracker_module.WATCH_LIST)
    for item in data:
        assert {"ticker", "price", "change_pct"} <= item.keys()


# --- /health ---

def test_health_returns_200(client):
    assert client.get("/health").status_code == 200


# --- /metrics ---

def test_metrics_returns_200(client):
    client.get("/")
    assert client.get("/metrics").status_code == 200


def test_metrics_contains_expected_metric_names(client):
    client.get("/")
    body = client.get("/metrics").data.decode()
    assert "etf_requests_total" in body
    assert "etf_ticker_fetch_success" in body


# --- error handling ---

def test_one_failed_ticker_still_returns_200(mocker):
    mocker.patch("tracker.fetch_ticker", side_effect=_mock_fetch(fail_ticker="RELIANCE.NS"))
    with app.test_client() as c:
        assert c.get("/").status_code == 200


def test_failed_ticker_has_error_field(mocker):
    mocker.patch("tracker.fetch_ticker", side_effect=_mock_fetch(fail_ticker="RELIANCE.NS"))
    with app.test_client() as c:
        data = json.loads(c.get("/").data)
    failed = next(d for d in data if d["ticker"] == "RELIANCE.NS")
    assert "error" in failed
    assert "price" not in failed


def test_other_tickers_unaffected_by_one_failure(mocker):
    mocker.patch("tracker.fetch_ticker", side_effect=_mock_fetch(fail_ticker="RELIANCE.NS"))
    with app.test_client() as c:
        data = json.loads(c.get("/").data)
    ok = [d for d in data if d["ticker"] != "RELIANCE.NS"]
    assert len(ok) == len(tracker_module.WATCH_LIST) - 1
    for item in ok:
        assert "price" in item
        assert "change_pct" in item
