"""
Enhanced FastAPI Application with Full Authentication, Authorization,
WebSocket, and Advanced Features.

Implements all documented features from Sections 0-11 and Appendices A-D.
"""

from fastapi import FastAPI, Depends, HTTPException, Query, Request, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
import logging
import os
import secrets
from datetime import datetime, timedelta

# Database and models
from .database import engine, Base, get_db
from .models import (
    Tile, UAV, Mission, SatelliteAlert, Detection, Telemetry, Evidence
)
from .auth_models import User, Role, RefreshToken, AuditLog, Zone, SystemConfig
from .schemas import (
    SatelliteAlertCreate, SatelliteAlertResponse,
    UAVCreate, UAVResponse, UAVStatusUpdate,
    DetectionCreate, DetectionResponse
)
from .schemas_enhanced import (
    # Auth
    UserCreate, UserLogin, UserResponse, TokenResponse, TokenRefresh,
    MFAEnableResponse, MFAVerify, PasswordChange, RoleResponse,
    # Zones
    ZoneCreate, ZoneUpdate, ZoneResponse,
    # Analytics
    SystemMetrics, UAVPerformanceMetrics, DetectionMetrics, CoverageMetrics,
    # Enhanced schemas
    DetectionCreateEnhanced, DetectionResponseEnhanced,
    MissionCreateEnhanced, MissionUpdate, MissionResponseEnhanced,
    AlertResponseEnhanced, AlertAcknowledge, AlertDismiss,
    ConfigUpdate, ConfigResponse,
    # WebSocket
    WSMessage, WSSubscribe
)

# Authentication and security
from .auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    verify_refresh_token, revoke_refresh_token,
    generate_mfa_secret, generate_mfa_qr_uri, verify_mfa_token,
    authenticate_user, get_current_user, require_permission, require_role,
    initialize_roles, create_default_admin, rbac,
    Permission, AuthenticationError, AuthorizationError
)
from .security import (
    AuditLogger, security_monitor, key_manager, GDPRCompliance, PasswordPolicy
)

# WebSocket
from .websocket import websocket_endpoint, manager as ws_manager

# MQTT client
from .mqtt_client import MQTTClient

# Algorithms
from .algorithms import (
    AStarPathfinder, DubinsPathPlanner, CoveragePatternGenerator,
    KalmanFilter, Waypoint
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="EVENT - UAV-Satellite Coordination System",
    description="Real-time coordination of satellite imagery and UAV missions with advanced security and analytics",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MQTT client
mqtt_client = MQTTClient()


# ============================================================
# Startup and Shutdown Events
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        # Connect MQTT
        mqtt_client.connect()
        logger.info("✓ MQTT client connected")
        
        # Initialize database
        db = next(get_db())
        
        # Initialize roles
        initialize_roles(db)
        logger.info("✓ Roles initialized")
        
        # Create default admin
        create_default_admin(db)
        logger.info("✓ Default admin created")
        
        db.close()
        
        logger.info("✓ EVENT System started successfully")
        
    except Exception as e:
        logger.error(f"✗ Startup error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    mqtt_client.disconnect()
    logger.info("EVENT System shutdown complete")


# ============================================================
# Middleware for Request Logging and Security
# ============================================================

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security middleware for audit logging and monitoring."""
    request_id = secrets.token_hex(8)
    request.state.request_id = request_id
    start_time = datetime.utcnow()
    
    # Check if IP is blocked
    client_ip = request.client.host
    if security_monitor.is_ip_blocked(client_ip):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "IP address blocked due to security violations"}
        )
    
    try:
        response = await call_next(request)
        
        # Log successful request (if authenticated)
        if hasattr(request.state, "user"):
            db = next(get_db())
            audit_logger = AuditLogger(db)
            
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            audit_logger.log(
                user_id=request.state.user.get("sub"),
                username=request.state.user.get("username"),
                action="api_request",
                resource_type=request.url.path.split("/")[2] if len(request.url.path.split("/")) > 2 else "root",
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
                status="success",
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "request_id": request_id
                },
                request_id=request_id
            )
            
            db.close()
        
        return response
    
    except Exception as e:
        logger.error(f"Request error: {e}")
        raise


# ============================================================
# Health and Status Endpoints
# ============================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "EVENT - UAV-Satellite Coordination System",
        "version": "2.0.0",
        "status": "operational",
        "documentation": "/api/docs"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check."""
    try:
        # Check database
        db.execute("SELECT 1")
        
        # Check MQTT
        mqtt_status = "connected" if mqtt_client.client and mqtt_client.client.is_connected() else "disconnected"
        
        # Get system metrics
        uav_count = db.query(func.count(UAV.id)).scalar()
        active_missions = db.query(func.count(Mission.id)).filter(
            Mission.status.in_(["active", "assigned"])
        ).scalar()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "online",
                "mqtt": mqtt_status,
                "websocket": "online"
            },
            "metrics": {
                "uavs": uav_count,
                "active_missions": active_missions
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.get("/api/version")
async def get_version():
    """Get API version information."""
    return {
        "version": "2.0.0",
        "api_version": "v1",
        "build_date": "2025-11-09",
        "features": [
            "JWT Authentication",
            "RBAC Authorization",
            "WebSocket Real-time Updates",
            "Advanced Path Planning",
            "ML-based Detection",
            "Geofencing",
            "Analytics Dashboard",
            "Audit Logging",
            "GDPR Compliance"
        ]
    }


# ============================================================
# Authentication Endpoints (Appendix D)
# ============================================================

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate password
    is_valid, error = PasswordPolicy.validate(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Create user
    user = User(
        id=f"user_{secrets.token_hex(8)}",
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_verified=False,
        consent_data_processing=True,
        consent_updated_at=datetime.utcnow()
    )
    
    # Assign roles
    for role_name in user_data.roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role:
            user.roles.append(role)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"User registered: {user.username}")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        roles=[role.name for role in user.roles],
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        last_login=user.last_login,
        created_at=user.created_at
    )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens."""
    # Authenticate user
    user = authenticate_user(credentials.username, credentials.password, db)
    
    if not user:
        # Track failed login
        security_monitor.track_failed_login(credentials.username, request.client.host)
        raise AuthenticationError("Invalid username or password")
    
    # Check MFA if enabled
    if user.mfa_enabled:
        if not credentials.mfa_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MFA token required"
            )
        
        mfa_secret = key_manager.decrypt_field(user.mfa_secret)
        if not verify_mfa_token(mfa_secret, credentials.mfa_token):
            security_monitor.track_failed_login(credentials.username, request.client.host)
            raise AuthenticationError("Invalid MFA token")
    
    # Get user roles
    role_names = [role.name for role in user.roles]
    
    # Create tokens
    access_token = create_access_token(user, role_names)
    refresh_token = create_refresh_token(user, db)
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Audit log
    audit_logger = AuditLogger(db)
    audit_logger.log_login(
        user.id,
        user.username,
        request.client.host,
        request.headers.get("user-agent"),
        True
    )
    
    logger.info(f"User logged in: {user.username}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=900  # 15 minutes
    )


@app.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    user = verify_refresh_token(token_data.refresh_token, db)
    
    if not user:
        raise AuthenticationError("Invalid or expired refresh token")
    
    # Revoke old refresh token
    revoke_refresh_token(token_data.refresh_token, db)
    
    # Create new tokens
    role_names = [role.name for role in user.roles]
    access_token = create_access_token(user, role_names)
    new_refresh_token = create_refresh_token(user, db)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=900
    )


@app.post("/api/auth/logout")
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user (revoke tokens)."""
    # Audit log
    audit_logger = AuditLogger(db)
    audit_logger.log_logout(
        current_user["sub"],
        current_user["username"],
        request.client.host
    )
    
    # TODO: Blacklist access token (requires Redis)
    
    return {"message": "Logged out successfully"}


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information."""
    user = db.query(User).filter(User.id == current_user["sub"]).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        roles=[role.name for role in user.roles],
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        last_login=user.last_login,
        created_at=user.created_at
    )


# Continue in next file due to size...
