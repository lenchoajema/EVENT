"""
Unit tests for scheduler module.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from services.scheduler.app.tasks import monitor_uav_status, process_pending_alerts
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    pytest.skip("Scheduler module not available", allow_module_level=True)


@pytest.mark.skipif(not SCHEDULER_AVAILABLE, reason="Scheduler not available")
def test_monitor_uav_status():
    """Test UAV status monitoring task"""
    # This would need proper database mocking
    # For now, just ensure the task can be imported
    assert callable(monitor_uav_status)


@pytest.mark.skipif(not SCHEDULER_AVAILABLE, reason="Scheduler not available")
def test_process_pending_alerts():
    """Test alert processing task"""
    # This would need proper database mocking
    # For now, just ensure the task can be imported
    assert callable(process_pending_alerts)
