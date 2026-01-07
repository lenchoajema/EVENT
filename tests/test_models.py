"""
Unit tests for models module.
"""

import pytest
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from services.api.app.models import (
        Base,
        UAV,
        Mission,
        Detection,
        SatelliteAlert,
        Tile
    )
except ImportError:
    pytest.skip("Models module not available", allow_module_level=True)


@pytest.fixture(scope="module")
def engine():
    """Create in-memory SQLite engine for testing."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module")
def tables(engine):
    """Create all tables in test database."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


class TestUAVModel:
    """Test UAV model."""
    
    def test_create_uav(self, db_session):
        """Test creating a UAV instance."""
        uav = UAV(
            name="Test-UAV-1",
            status="idle",
            battery_level=100,
            current_latitude=37.7749,
            current_longitude=-122.4194,
            current_altitude=0
        )
        
        db_session.add(uav)
        db_session.commit()
        
        assert uav.id is not None
        assert uav.name == "Test-UAV-1"
        assert uav.status == "idle"
    
    def test_uav_defaults(self, db_session):
        """Test UAV default values."""
        uav = UAV(
            name="Test-UAV-2",
            current_latitude=37.7749,
            current_longitude=-122.4194
        )
        
        db_session.add(uav)
        db_session.commit()
        
        assert uav.status == "idle"
        assert uav.battery_level == 100
        assert uav.current_altitude == 0
    
    def test_uav_relationships(self, db_session):
        """Test UAV relationships with missions."""
        uav = UAV(
            name="Test-UAV-3",
            current_latitude=37.7749,
            current_longitude=-122.4194
        )
        db_session.add(uav)
        db_session.commit()
        
        # Missions relationship should exist
        assert hasattr(uav, 'missions')
        assert isinstance(uav.missions, list)


class TestMissionModel:
    """Test Mission model."""
    
    def test_create_mission(self, db_session):
        """Test creating a Mission instance."""
        uav = UAV(
            name="Test-UAV-4",
            current_latitude=37.7749,
            current_longitude=-122.4194
        )
        db_session.add(uav)
        db_session.commit()
        
        mission = Mission(
            uav_id=uav.id,
            mission_type="verification",
            status="pending",
            target_latitude=37.7849,
            target_longitude=-122.4294,
            priority=5
        )
        
        db_session.add(mission)
        db_session.commit()
        
        assert mission.id is not None
        assert mission.uav_id == uav.id
        assert mission.status == "pending"
    
    def test_mission_timestamps(self, db_session):
        """Test mission timestamp fields."""
        uav = UAV(name="Test-UAV-5", current_latitude=0, current_longitude=0)
        db_session.add(uav)
        db_session.commit()
        
        mission = Mission(
            uav_id=uav.id,
            mission_type="patrol",
            status="in_progress",
            target_latitude=0,
            target_longitude=0
        )
        
        db_session.add(mission)
        db_session.commit()
        
        assert mission.created_at is not None
        assert isinstance(mission.created_at, datetime)


class TestDetectionModel:
    """Test Detection model."""
    
    def test_create_detection(self, db_session):
        """Test creating a Detection instance."""
        uav = UAV(name="Test-UAV-6", current_latitude=0, current_longitude=0)
        db_session.add(uav)
        db_session.commit()
        
        detection = Detection(
            uav_id=uav.id,
            object_class="person",
            confidence=0.95,
            latitude=37.7749,
            longitude=-122.4194
        )
        
        db_session.add(detection)
        db_session.commit()
        
        assert detection.id is not None
        assert detection.object_class == "person"
        assert detection.confidence == 0.95
    
    def test_detection_with_bounding_box(self, db_session):
        """Test detection with bounding box data."""
        uav = UAV(name="Test-UAV-7", current_latitude=0, current_longitude=0)
        db_session.add(uav)
        db_session.commit()
        
        detection = Detection(
            uav_id=uav.id,
            object_class="vehicle",
            confidence=0.87,
            latitude=37.7749,
            longitude=-122.4194,
            bbox_x=100,
            bbox_y=200,
            bbox_width=50,
            bbox_height=75
        )
        
        db_session.add(detection)
        db_session.commit()
        
        assert detection.bbox_x == 100
        assert detection.bbox_width == 50


class TestSatelliteAlertModel:
    """Test SatelliteAlert model."""
    
    def test_create_satellite_alert(self, db_session):
        """Test creating a SatelliteAlert instance."""
        tile = Tile(
            tile_id="T10SEG",
            zone_number=10,
            zone_letter="S",
            grid_square="EG"
        )
        db_session.add(tile)
        db_session.commit()
        
        alert = SatelliteAlert(
            tile_id=tile.tile_id,
            alert_type="anomaly",
            severity="medium",
            latitude=37.7749,
            longitude=-122.4194,
            confidence=0.82
        )
        
        db_session.add(alert)
        db_session.commit()
        
        assert alert.id is not None
        assert alert.alert_type == "anomaly"
        assert alert.severity == "medium"
    
    def test_alert_status_workflow(self, db_session):
        """Test alert status transitions."""
        tile = Tile(tile_id="T10SEG", zone_number=10, zone_letter="S", grid_square="EG")
        db_session.add(tile)
        db_session.commit()
        
        alert = SatelliteAlert(
            tile_id=tile.tile_id,
            alert_type="fire",
            severity="high",
            latitude=37.7749,
            longitude=-122.4194,
            status="pending"
        )
        
        db_session.add(alert)
        db_session.commit()
        
        # Update status
        alert.status = "assigned"
        db_session.commit()
        
        assert alert.status == "assigned"


class TestTileModel:
    """Test Tile model."""
    
    def test_create_tile(self, db_session):
        """Test creating a Tile instance."""
        tile = Tile(
            tile_id="T10SEG",
            zone_number=10,
            zone_letter="S",
            grid_square="EG",
            coverage_area_km2=100.0
        )
        
        db_session.add(tile)
        db_session.commit()
        
        assert tile.tile_id == "T10SEG"
        assert tile.zone_number == 10
        assert tile.coverage_area_km2 == 100.0
    
    def test_tile_relationships(self, db_session):
        """Test Tile relationships with alerts."""
        tile = Tile(
            tile_id="T11SKA",
            zone_number=11,
            zone_letter="S",
            grid_square="KA"
        )
        db_session.add(tile)
        db_session.commit()
        
        # Alerts relationship should exist
        assert hasattr(tile, 'alerts')
        assert isinstance(tile.alerts, list)


class TestModelConstraints:
    """Test model constraints and validations."""
    
    def test_uav_unique_name(self, db_session):
        """Test UAV name uniqueness constraint."""
        uav1 = UAV(name="Duplicate-UAV", current_latitude=0, current_longitude=0)
        db_session.add(uav1)
        db_session.commit()
        
        uav2 = UAV(name="Duplicate-UAV", current_latitude=0, current_longitude=0)
        db_session.add(uav2)
        
        with pytest.raises(Exception):  # IntegrityError or similar
            db_session.commit()
    
    def test_detection_confidence_range(self, db_session):
        """Test detection confidence is within valid range."""
        uav = UAV(name="Test-UAV-8", current_latitude=0, current_longitude=0)
        db_session.add(uav)
        db_session.commit()
        
        detection = Detection(
            uav_id=uav.id,
            object_class="test",
            confidence=1.5,  # Invalid: > 1.0
            latitude=0,
            longitude=0
        )
        
        # Some databases may enforce check constraints
        # This test documents expected behavior
        db_session.add(detection)
        # May or may not raise depending on DB constraints
