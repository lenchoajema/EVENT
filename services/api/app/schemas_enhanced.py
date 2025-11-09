"""
Enhanced Pydantic schemas for authentication, authorization, and advanced features.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================
# Authentication & Authorization Schemas
# ============================================================

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    roles: List[str] = ["viewer"]  # Default role


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str
    mfa_token: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    roles: List[str]
    is_active: bool
    mfa_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class MFAEnableResponse(BaseModel):
    """Schema for MFA enablement response."""
    secret: str
    qr_uri: str
    backup_codes: List[str]


class MFAVerify(BaseModel):
    """Schema for MFA verification."""
    token: str


class PasswordChange(BaseModel):
    """Schema for password change."""
    old_password: str
    new_password: str = Field(..., min_length=8)


class RoleResponse(BaseModel):
    """Schema for role data."""
    id: str
    name: str
    description: Optional[str]
    permissions: List[str]
    
    class Config:
        from_attributes = True


# ============================================================
# Zone Management Schemas
# ============================================================

class ZoneTier(str, Enum):
    """Zone access tier classification."""
    PUBLIC = "public"
    RESTRICTED = "restricted"
    PROHIBITED = "prohibited"


class ZoneType(str, Enum):
    """Zone type classification."""
    BORDER = "border"
    INFRASTRUCTURE = "infrastructure"
    PROTECTED_AREA = "protected_area"
    MILITARY = "military"
    AIRPORT = "airport"
    URBAN = "urban"
    WILDERNESS = "wilderness"


class ZoneCreate(BaseModel):
    """Schema for creating a zone."""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    geometry: Dict[str, Any]  # GeoJSON polygon
    tier: ZoneTier
    zone_type: ZoneType
    priority: int = Field(default=0, ge=0, le=10)
    monitoring_enabled: bool = True
    alert_on_entry: bool = False
    metadata: Optional[Dict[str, Any]] = None


class ZoneUpdate(BaseModel):
    """Schema for updating a zone."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    geometry: Optional[Dict[str, Any]] = None
    tier: Optional[ZoneTier] = None
    zone_type: Optional[ZoneType] = None
    priority: Optional[int] = Field(None, ge=0, le=10)
    monitoring_enabled: Optional[bool] = None
    alert_on_entry: Optional[bool] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ZoneResponse(BaseModel):
    """Schema for zone response."""
    id: int
    zone_id: str
    name: str
    description: Optional[str]
    geometry: Dict[str, Any]
    center_lat: Optional[float]
    center_lon: Optional[float]
    area_km2: Optional[float]
    tier: str
    zone_type: str
    is_active: bool
    priority: int
    monitoring_enabled: bool
    alert_on_entry: bool
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# Analytics & Metrics Schemas
# ============================================================

class SystemMetrics(BaseModel):
    """System-wide metrics."""
    timestamp: datetime
    uavs_total: int
    uavs_available: int
    uavs_in_mission: int
    missions_active: int
    missions_completed_24h: int
    detections_24h: int
    alerts_active: int
    coverage_percent: float
    avg_response_time_seconds: Optional[float]


class UAVPerformanceMetrics(BaseModel):
    """UAV performance metrics."""
    uav_id: str
    missions_completed: int
    total_flight_time_hours: float
    avg_mission_duration_minutes: float
    detections_made: int
    avg_battery_efficiency: float
    reliability_score: float


class DetectionMetrics(BaseModel):
    """Detection performance metrics."""
    total_detections: int
    verified_detections: int
    false_positives: int
    precision: float
    recall: float
    f1_score: float
    avg_confidence: float
    detection_by_class: Dict[str, int]


class CoverageMetrics(BaseModel):
    """Coverage analysis metrics."""
    total_area_km2: float
    monitored_area_km2: float
    coverage_percent: float
    gaps_count: int
    redundancy_score: float
    tiles_monitored: int
    tiles_unmonitored: int


class ResponseTimeMetrics(BaseModel):
    """Response time metrics."""
    avg_detection_to_alert_seconds: float
    avg_alert_to_dispatch_seconds: float
    avg_dispatch_to_arrival_seconds: float
    avg_end_to_end_seconds: float
    percentile_90_seconds: float
    percentile_95_seconds: float
    target_compliance_percent: float


# ============================================================
# Advanced Detection Schemas
# ============================================================

class DetectionClass(str, Enum):
    """Detection classes."""
    PERSON = "person"
    VEHICLE = "vehicle"
    ANIMAL = "animal"
    FIRE = "fire"
    SMOKE = "smoke"
    BUILDING = "building"
    UNKNOWN = "unknown"


class ThreatLevel(str, Enum):
    """Threat level classification."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionCreateEnhanced(BaseModel):
    """Enhanced detection creation schema."""
    uav_id: str
    mission_id: Optional[str] = None
    detection_class: DetectionClass
    confidence: float = Field(..., ge=0.0, le=1.0)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    bbox: Dict[str, float]  # {x, y, width, height}
    image_url: Optional[str] = None
    threat_level: ThreatLevel = ThreatLevel.NONE
    track_id: Optional[str] = None  # For Kalman filter tracking
    metadata: Optional[Dict[str, Any]] = None


class DetectionResponseEnhanced(BaseModel):
    """Enhanced detection response schema."""
    id: int
    detection_id: str
    uav_id: str
    mission_id: Optional[str]
    detection_class: str
    confidence: float
    latitude: float
    longitude: float
    bbox: Dict[str, float]
    image_url: Optional[str]
    threat_level: str
    track_id: Optional[str]
    verified: bool
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# Mission Management Schemas
# ============================================================

class MissionType(str, Enum):
    """Mission type."""
    PATROL = "patrol"
    INVESTIGATION = "investigation"
    SEARCH = "search"
    SURVEILLANCE = "surveillance"
    EMERGENCY_RESPONSE = "emergency_response"


class MissionStatus(str, Enum):
    """Mission status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"


class WaypointCreate(BaseModel):
    """Waypoint schema."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: float = Field(..., ge=0, le=500)
    speed: Optional[float] = Field(None, ge=0, le=30)
    heading: Optional[float] = Field(None, ge=0, le=360)
    action: Optional[str] = None  # hover, scan, photo, etc.


class MissionCreateEnhanced(BaseModel):
    """Enhanced mission creation schema."""
    mission_type: MissionType
    uav_id: Optional[str] = None  # Auto-assigned if None
    zone_id: Optional[str] = None
    tile_id: Optional[str] = None
    priority: int = Field(default=5, ge=1, le=10)
    waypoints: List[WaypointCreate]
    parameters: Optional[Dict[str, Any]] = None  # Mission-specific params
    estimated_duration_minutes: Optional[int] = None


class MissionUpdate(BaseModel):
    """Mission update schema."""
    status: Optional[MissionStatus] = None
    waypoints: Optional[List[WaypointCreate]] = None
    parameters: Optional[Dict[str, Any]] = None


class MissionResponseEnhanced(BaseModel):
    """Enhanced mission response schema."""
    id: int
    mission_id: str
    mission_type: str
    uav_id: Optional[str]
    zone_id: Optional[str]
    tile_id: Optional[str]
    status: str
    priority: int
    waypoints: List[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    estimated_duration: Optional[int]
    actual_duration: Optional[int]
    detections_count: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# Alert Management Schemas
# ============================================================

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status."""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    DISMISSED = "dismissed"


class AlertAcknowledge(BaseModel):
    """Alert acknowledgement schema."""
    notes: Optional[str] = None


class AlertDismiss(BaseModel):
    """Alert dismissal schema."""
    reason: str
    notes: Optional[str] = None


class AlertResponseEnhanced(BaseModel):
    """Enhanced alert response schema."""
    id: int
    alert_id: str
    alert_type: str
    severity: str
    status: str
    confidence: float
    latitude: Optional[float]
    longitude: Optional[float]
    zone_id: Optional[str]
    priority: int
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# System Configuration Schemas
# ============================================================

class ConfigUpdate(BaseModel):
    """System configuration update."""
    key: str
    value: Any
    description: Optional[str] = None
    category: Optional[str] = None


class ConfigResponse(BaseModel):
    """System configuration response."""
    id: int
    key: str
    value: Any
    description: Optional[str]
    category: Optional[str]
    updated_by: Optional[str]
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# WebSocket Message Schemas
# ============================================================

class WSMessageType(str, Enum):
    """WebSocket message types."""
    AUTH = "auth"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    TELEMETRY = "telemetry"
    DETECTION = "detection"
    ALERT = "alert"
    MISSION_UPDATE = "mission_update"
    SYSTEM_STATUS = "system_status"
    ERROR = "error"


class WSMessage(BaseModel):
    """WebSocket message schema."""
    type: WSMessageType
    timestamp: Optional[datetime] = None
    data: Optional[Dict[str, Any]] = None


class WSSubscribe(BaseModel):
    """WebSocket subscription request."""
    channels: List[str]  # telemetry, alerts, detections, etc.


class WSTelemetry(BaseModel):
    """WebSocket telemetry data."""
    uav_id: str
    latitude: float
    longitude: float
    altitude: float
    battery_percent: float
    speed: float
    heading: float
    status: str
    timestamp: datetime
