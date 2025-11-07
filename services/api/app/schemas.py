from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Satellite Alert Schemas
class SatelliteAlertCreate(BaseModel):
    alert_type: str
    severity: str
    latitude: float
    longitude: float
    description: Optional[str] = None

class SatelliteAlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    latitude: float
    longitude: float
    description: Optional[str]
    created_at: datetime
    status: str
    assigned_uav_id: Optional[int]

    class Config:
        from_attributes = True

# UAV Schemas
class UAVCreate(BaseModel):
    name: str
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None

class UAVStatusUpdate(BaseModel):
    status: Optional[str] = None
    battery_level: Optional[float] = None
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None

class UAVResponse(BaseModel):
    id: int
    name: str
    status: str
    battery_level: float
    current_latitude: Optional[float]
    current_longitude: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Detection Schemas
class DetectionCreate(BaseModel):
    uav_id: int
    alert_id: Optional[int] = None
    object_class: str
    confidence: float
    latitude: float
    longitude: float
    image_path: Optional[str] = None
    metadata: Optional[str] = None

class DetectionResponse(BaseModel):
    id: int
    uav_id: int
    alert_id: Optional[int]
    object_class: str
    confidence: float
    latitude: float
    longitude: float
    image_path: Optional[str]
    metadata: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
