"""
Unit tests for Prometheus metrics.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from services.api.app.simple_metrics import metrics, root
    from prometheus_client import generate_latest
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    pytest.skip("Metrics module not available", allow_module_level=True)


@pytest.mark.skipif(not METRICS_AVAILABLE, reason="Metrics module not available")
def test_simple_metrics_endpoint_direct_call():
    """Test metrics endpoint returns Prometheus format."""
    # Call the endpoint function directly to avoid TestClient/httpx dependency in this test env
    response = metrics()
    assert response.status_code == 200
    ct = response.media_type or response.headers.get("content-type", "")
    assert "text/plain" in ct


@pytest.mark.skipif(not METRICS_AVAILABLE, reason="Metrics module not available")
def test_root_direct_call():
    """Test root endpoint returns status message."""
    r = root()
    assert isinstance(r, dict)
    assert r.get("message") == "simple metrics app operational"
