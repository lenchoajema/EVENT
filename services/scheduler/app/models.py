from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
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
    status = Column(String, default="pending")
    assigned_uav_id = Column(Integer, ForeignKey("uavs.id"), nullable=True)

class UAV(Base):
    __tablename__ = "uavs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    status = Column(String, default="idle")
    battery_level = Column(Float, default=100.0)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    current_location = Column(Geometry('POINT', srid=4326), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
