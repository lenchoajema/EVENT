from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from geoalchemy2 import Geometry

from .database import Base

# Import auth models to ensure they're registered
from .auth_models import User, Role, RefreshToken, AuditLog, Zone, SystemConfig, user_roles


class Tile(Base):
    """Geographic tiles for satellite monitoring coverage."""
    __tablename__ = "tiles"

    id = Column(Integer, primary_key=True, index=True)
    tile_id = Column(String(50), unique=True, nullable=False, index=True)
    geometry = Column(Geometry('POLYGON', srid=4326), nullable=False)
    center_lat = Column(Float, nullable=False)
    center_lon = Column(Float, nullable=False)
    priority = Column(Integer, default=0, index=True)
    status = Column(String(20), default="unmonitored", index=True)  # unmonitored, monitored, investigating
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    missions = relationship("Mission", back_populates="tile")
    alerts = relationship("SatelliteAlert", back_populates="tile")


class UAV(Base):
    """UAV fleet registry and status."""
    __tablename__ = "uavs"

    id = Column(Integer, primary_key=True, index=True)
    uav_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    position = Column(Geometry('POINT', srid=4326))
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float, default=0)
    battery_level = Column(Float, default=100.0, index=True)
    status = Column(String(20), default="available", index=True)  # available, assigned, in_mission, returning, charging
    mission_id = Column(Integer)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    missions = relationship("Mission", back_populates="uav")
    detections = relationship("Detection", back_populates="uav")
    telemetry = relationship("Telemetry", back_populates="uav")


class Mission(Base):
    """UAV mission assignments and tracking."""
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(String(50), unique=True, nullable=False, index=True)
    uav_id = Column(String(50), ForeignKey("uavs.uav_id"))
    tile_id = Column(String(50), ForeignKey("tiles.tile_id"))
    status = Column(String(20), default="pending", index=True)  # pending, assigned, active, completed, failed
    priority = Column(Integer, default=0)
    waypoints = Column(JSON)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    estimated_duration = Column(Integer)  # in seconds
    actual_duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    uav = relationship("UAV", back_populates="missions")
    tile = relationship("Tile", back_populates="missions")
    detections = relationship("Detection", back_populates="mission")


class SatelliteAlert(Base):
    """Satellite detection alerts requiring UAV verification."""
    __tablename__ = "sat_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(50), unique=True, nullable=False, index=True)
    tile_id = Column(String(50), ForeignKey("tiles.tile_id"))
    alert_type = Column(String(50), nullable=False, index=True)
    event_type = Column(String(50))
    confidence = Column(Float)
    position = Column(Geometry('POINT', srid=4326))
    latitude = Column(Float)
    longitude = Column(Float)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    priority = Column(Integer, default=0, index=True)
    status = Column(String(20), default="new", index=True)  # new, assigned, investigating, verified, false_positive
    meta_data = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    tile = relationship("Tile", back_populates="alerts")


class Detection(Base):
    """UAV edge inference detections (YOLOv8 results)."""
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(String(50), unique=True, nullable=False, index=True)
    uav_id = Column(String(50), ForeignKey("uavs.uav_id"))
    mission_id = Column(String(50), ForeignKey("missions.mission_id"))
    detection_type = Column(String(50), nullable=False, index=True)  # person, vehicle, fire, etc.
    confidence = Column(Float, nullable=False, index=True)
    position = Column(Geometry('POINT', srid=4326))
    latitude = Column(Float)
    longitude = Column(Float)
    bbox = Column(JSON)  # Bounding box coordinates
    image_url = Column(String(500))
    meta_data = Column(JSON)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    uav = relationship("UAV", back_populates="detections")
    mission = relationship("Mission", back_populates="detections")
    evidence = relationship("Evidence", back_populates="detection")


class Telemetry(Base):
    """Real-time UAV telemetry data."""
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    uav_id = Column(String(50), ForeignKey("uavs.uav_id"))
    position = Column(Geometry('POINT', srid=4326))
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    battery_level = Column(Float)
    speed = Column(Float)
    heading = Column(Float)
    status = Column(String(20))
    meta_data = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    uav = relationship("UAV", back_populates="telemetry")


class Evidence(Base):
    """Evidence storage references (MinIO paths)."""
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(String(50), unique=True, nullable=False, index=True)
    detection_id = Column(String(50), ForeignKey("detections.detection_id"))
    mission_id = Column(String(50), ForeignKey("missions.mission_id"))
    evidence_type = Column(String(50), nullable=False, index=True)  # image, video, log, etc.
    storage_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    checksum = Column(String(100))
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    detection = relationship("Detection", back_populates="evidence")

