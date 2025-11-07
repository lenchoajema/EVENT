from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from geoalchemy2 import Geometry

from .database import Base

class SatelliteAlert(Base):
    __tablename__ = "satellite_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geometry('POINT', srid=4326))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, assigned, investigating, resolved
    assigned_uav_id = Column(Integer, ForeignKey("uavs.id"), nullable=True)

    assigned_uav = relationship("UAV", back_populates="assigned_alerts")
    detections = relationship("Detection", back_populates="alert")

class UAV(Base):
    __tablename__ = "uavs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    status = Column(String, default="idle")  # idle, assigned, flying, charging
    battery_level = Column(Float, default=100.0)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    current_location = Column(Geometry('POINT', srid=4326), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_alerts = relationship("SatelliteAlert", back_populates="assigned_uav")
    detections = relationship("Detection", back_populates="uav")

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    uav_id = Column(Integer, ForeignKey("uavs.id"), nullable=False)
    alert_id = Column(Integer, ForeignKey("satellite_alerts.id"), nullable=True)
    object_class = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geometry('POINT', srid=4326))
    image_path = Column(String, nullable=True)
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    uav = relationship("UAV", back_populates="detections")
    alert = relationship("SatelliteAlert", back_populates="detections")
