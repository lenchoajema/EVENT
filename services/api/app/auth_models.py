"""
Authentication and Authorization Models.

Implements user management, roles, permissions, and audit logging
as specified in Appendix D: Security Plan.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from .database import Base


# Many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String(50), ForeignKey('users.id'), primary_key=True),
    Column('role_id', String(50), ForeignKey('roles.id'), primary_key=True)
)


class Permission(str, Enum):
    """System permissions as defined in Appendix D."""
    # Detections
    DETECTIONS_READ = "detections:read"
    DETECTIONS_CREATE = "detections:create"
    DETECTIONS_UPDATE = "detections:update"
    DETECTIONS_DELETE = "detections:delete"
    
    # Alerts
    ALERTS_READ = "alerts:read"
    ALERTS_CREATE = "alerts:create"
    ALERTS_ACKNOWLEDGE = "alerts:acknowledge"
    ALERTS_DISMISS = "alerts:dismiss"
    
    # Missions
    MISSIONS_READ = "missions:read"
    MISSIONS_CREATE = "missions:create"
    MISSIONS_UPDATE = "missions:update"
    MISSIONS_ABORT = "missions:abort"
    
    # UAVs
    UAVS_READ = "uavs:read"
    UAVS_COMMAND = "uavs:command"
    UAVS_CONFIGURE = "uavs:configure"
    
    # Zones
    ZONES_READ = "zones:read"
    ZONES_MANAGE = "zones:manage"
    
    # Analytics
    ANALYTICS_READ = "analytics:read"
    
    # System
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"
    USERS_MANAGE = "users:manage"


class User(Base):
    """User accounts with authentication credentials."""
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    
    # MFA fields
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(Text)  # Encrypted TOTP secret
    
    # API access
    api_key = Column(Text)  # Encrypted API key
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # GDPR consent
    consent_data_processing = Column(Boolean, default=False)
    consent_analytics = Column(Boolean, default=False)
    consent_third_party = Column(Boolean, default=False)
    consent_marketing = Column(Boolean, default=False)
    consent_updated_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")


class Role(Base):
    """User roles with associated permissions."""
    __tablename__ = "roles"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    permissions = Column(JSON, nullable=False)  # List of Permission enums
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")


class RefreshToken(Base):
    """Refresh tokens for JWT authentication."""
    __tablename__ = "refresh_tokens"
    
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class AuditLog(Base):
    """Audit log entries for security monitoring."""
    __tablename__ = "audit_logs"
    
    id = Column(String(50), primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), index=True)
    username = Column(String(100))
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), index=True)
    resource_id = Column(String(100))
    ip_address = Column(String(50))
    user_agent = Column(Text)
    status = Column(String(20), nullable=False)  # success, failure
    details = Column(JSON)
    request_id = Column(String(50), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class Zone(Base):
    """Geographic zones with access tiers and geofencing."""
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Geometry
    geometry = Column(JSON, nullable=False)  # GeoJSON polygon
    center_lat = Column(Float)
    center_lon = Column(Float)
    area_km2 = Column(Float)
    
    # Classification (from Section 4)
    tier = Column(String(20), nullable=False, index=True)  # public, restricted, prohibited
    zone_type = Column(String(50), index=True)  # border, infrastructure, protected_area, etc.
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=0)
    
    # Monitoring
    monitoring_enabled = Column(Boolean, default=True)
    alert_on_entry = Column(Boolean, default=False)
    
    # Metadata (renamed to avoid SQLAlchemy reserved word)
    zone_metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SystemConfig(Base):
    """System configuration parameters."""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    description = Column(Text)
    category = Column(String(50), index=True)
    is_encrypted = Column(Boolean, default=False)
    updated_by = Column(String(50))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
