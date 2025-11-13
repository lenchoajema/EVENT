import pytest
from app.simple_metrics import metrics, root
from prometheus_client import generate_latest


def test_simple_metrics_endpoint_direct_call():
    # Call the endpoint function directly to avoid TestClient/httpx dependency in this test env
    response = metrics()
    assert response.status_code == 200
    ct = response.media_type or response.headers.get("content-type", "")
    assert "text/plain" in ct


def test_root_direct_call():
    r = root()
    assert isinstance(r, dict)
    assert r.get("message") == "simple metrics app operational"
