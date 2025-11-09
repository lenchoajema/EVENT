from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# Tile Schemas
class TileBase(BaseModel):
    tile_id: str
    center_lat: float
    center_lon: float
    priority: int = 0
    status: str = "unmonitored"


class TileResponse(TileBase):
    id: int
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Satellite Alert Schemas
class SatelliteAlertCreate(BaseModel):
    tile_id: Optional[str] = None
    alert_type: Optional[str] = "detection"
    event_type: str
    confidence: Optional[float] = None
    latitude: float
    longitude: float
    severity: str = "medium"
    priority: int = 5
    metadata: Optional[Dict[str, Any]] = None


class SatelliteAlertResponse(BaseModel):
    id: int
    alert_id: str
    tile_id: Optional[str]
    alert_type: str
    event_type: Optional[str]
    confidence: Optional[float]
    latitude: float
    longitude: float
    severity: str
    priority: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# UAV Schemas
class UAVCreate(BaseModel):
    uav_id: str
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    battery_level: float = 100.0


class UAVStatusUpdate(BaseModel):
    status: Optional[str] = None
    battery_level: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None


class UAVResponse(BaseModel):
    id: int
    uav_id: str
    name: str
    status: str
    battery_level: float
    latitude: Optional[float]
    longitude: Optional[float]
    altitude: Optional[float]
    last_seen: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Mission Schemas
class MissionCreate(BaseModel):
    mission_id: str
    uav_id: str
    tile_id: str
    priority: int = 5
    waypoints: Optional[List[Dict[str, Any]]] = None


class MissionResponse(BaseModel):
    id: int
    mission_id: str
    uav_id: str
    tile_id: str
    status: str
    priority: int
    waypoints: Optional[Dict[str, Any]]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Detection Schemas
class DetectionCreate(BaseModel):
    uav_id: str
    mission_id: Optional[str] = None
    detection_type: str
    confidence: float
    latitude: float
    longitude: float
    bbox: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DetectionResponse(BaseModel):
    id: int
    detection_id: str
    uav_id: str
    mission_id: Optional[str]
    detection_type: str
    confidence: float
    latitude: float
    longitude: float
    bbox: Optional[Dict[str, Any]]
    image_url: Optional[str]
    verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Telemetry Schemas
class TelemetryCreate(BaseModel):
    uav_id: str
    latitude: float
    longitude: float
    altitude: float
    battery_level: float
    speed: Optional[float] = None
    heading: Optional[float] = None
    status: str
    metadata: Optional[Dict[str, Any]] = None


class TelemetryResponse(BaseModel):
    id: int
    uav_id: str
    latitude: float
    longitude: float
    altitude: float
    battery_level: float
    speed: Optional[float]
    heading: Optional[float]
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True

