"""
Authentication and Authorization Utilities.

Implements JWT tokens, password hashing, MFA, and RBAC
as specified in Appendix D: Security Plan.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Set
import jwt
import pyotp
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .auth_models import User, Role, RefreshToken, Permission
from .database import get_db

# Blacklist support (Redis if available, otherwise in-memory)
import hashlib
try:
    import redis as _redis  # optional
except Exception:
    _redis = None


# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Password hashing - using bcrypt directly to avoid compatibility issues
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    if len(password) > 72:
        raise ValueError("Password too long (max 72 bytes)")
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    if len(plain_password) > 72:
        plain_password = plain_password[:72]
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# HTTP Bearer token
security = HTTPBearer()


class AuthenticationError(HTTPException):
    """Authentication error."""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(HTTPException):
    """Authorization error."""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


def create_access_token(user: User, roles: List[str]) -> str:
    """Create JWT access token."""
    # Collect permissions from all roles
    permissions = []
    for role in user.roles:
        permissions.extend(role.permissions)
    
    payload = {
        "sub": user.id,
        "username": user.username,
        "email": user.email,
        "roles": roles,
        "permissions": list(set(permissions)),  # Deduplicate
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iss": "event-auth-server",
        "aud": "event-api"
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user: User, db: Session) -> str:
    """Create and store refresh token."""
    # Generate token
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Store in database
    refresh_token = RefreshToken(
        id=f"rt_{secrets.token_hex(8)}",
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    db.add(refresh_token)
    db.commit()
    
    return token


def decode_access_token(token: str) -> dict:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience="event-api"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


# Access token blacklist manager
class AccessTokenBlacklist:
    def __init__(self):
        self._use_redis = False
        self._redis = None
        redis_url = os.getenv("REDIS_URL")
        if redis_url and _redis is not None:
            try:
                self._redis = _redis.from_url(redis_url)
                self._use_redis = True
            except Exception:
                self._use_redis = False

        # In-memory store: token_hash -> expiry_timestamp (float)
        self._store = {}

    def blacklist_token(self, token: str, expires_at: Optional[datetime] = None):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if self._use_redis:
            ttl = None
            if expires_at:
                ttl = int((expires_at - datetime.utcnow()).total_seconds())
            else:
                ttl = ACCESS_TOKEN_EXPIRE_MINUTES * 60
            if ttl < 0:
                ttl = 0
            try:
                self._redis.setex(f"blacklist:{token_hash}", ttl, "1")
            except Exception:
                # Redis failure should not block logout
                pass
        else:
            exp_ts = expires_at.timestamp() if expires_at else (datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
            self._store[token_hash] = exp_ts

    def is_blacklisted(self, token: str) -> bool:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if self._use_redis:
            try:
                return self._redis.get(f"blacklist:{token_hash}") is not None
            except Exception:
                return False
        else:
            exp_ts = self._store.get(token_hash)
            if not exp_ts:
                return False
            if exp_ts < datetime.utcnow().timestamp():
                # expired -> cleanup
                try:
                    del self._store[token_hash]
                except KeyError:
                    pass
                return False
            return True


# Global blacklist instance
token_blacklist = AccessTokenBlacklist()


def blacklist_access_token(token: str):
    """Blacklist an access token until its expiry. Non-fatal if decode fails."""
    try:
        # decode without verifying expiration to read exp claim
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience="event-api", options={"verify_exp": False})
        exp = payload.get("exp")
        expires_at = datetime.utcfromtimestamp(exp) if exp else None
    except Exception:
        expires_at = None

    token_blacklist.blacklist_token(token, expires_at)


def verify_refresh_token(token: str, db: Session) -> Optional[User]:
    """Verify refresh token and return user."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    if not refresh_token:
        return None
    
    return db.query(User).filter(User.id == refresh_token.user_id).first()


def revoke_refresh_token(token: str, db: Session):
    """Revoke a refresh token."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()
    
    if refresh_token:
        refresh_token.revoked = True
        db.commit()


# MFA Functions

def generate_mfa_secret() -> str:
    """Generate new MFA secret."""
    return pyotp.random_base32()


def generate_mfa_qr_uri(username: str, secret: str, issuer: str = "EVENT") -> str:
    """Generate QR code URI for authenticator app."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name=issuer)


def verify_mfa_token(secret: str, token: str) -> bool:
    """Verify TOTP token."""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)  # Allow 30s window


# RBAC Functions

class RBACManager:
    """Role-Based Access Control manager."""
    
    def __init__(self):
        self.role_permissions = {
            "viewer": [
                Permission.DETECTIONS_READ,
                Permission.ALERTS_READ,
                Permission.MISSIONS_READ,
                Permission.UAVS_READ,
                Permission.ZONES_READ,
                Permission.ANALYTICS_READ
            ],
            "operator": [
                Permission.DETECTIONS_READ,
                Permission.DETECTIONS_CREATE,
                Permission.ALERTS_READ,
                Permission.ALERTS_ACKNOWLEDGE,
                Permission.ALERTS_DISMISS,
                Permission.MISSIONS_READ,
                Permission.MISSIONS_CREATE,
                Permission.MISSIONS_UPDATE,
                Permission.UAVS_READ,
                Permission.UAVS_COMMAND,
                Permission.ZONES_READ,
                Permission.ANALYTICS_READ
            ],
            "supervisor": [
                Permission.DETECTIONS_READ,
                Permission.DETECTIONS_CREATE,
                Permission.DETECTIONS_UPDATE,
                Permission.DETECTIONS_DELETE,
                Permission.ALERTS_READ,
                Permission.ALERTS_CREATE,
                Permission.ALERTS_ACKNOWLEDGE,
                Permission.ALERTS_DISMISS,
                Permission.MISSIONS_READ,
                Permission.MISSIONS_CREATE,
                Permission.MISSIONS_UPDATE,
                Permission.MISSIONS_ABORT,
                Permission.UAVS_READ,
                Permission.UAVS_COMMAND,
                Permission.UAVS_CONFIGURE,
                Permission.ZONES_READ,
                Permission.ZONES_MANAGE,
                Permission.ANALYTICS_READ,
                Permission.SYSTEM_CONFIG
            ],
            "admin": list(Permission)  # All permissions
        }
    
    def check_permission(self, user_permissions: List[str], required_permission: Permission) -> bool:
        """Check if user has required permission."""
        return required_permission.value in user_permissions
    
    def get_role_permissions(self, role_name: str) -> List[str]:
        """Get permissions for a role."""
        permissions = self.role_permissions.get(role_name, [])
        return [p.value for p in permissions]


rbac = RBACManager()


# FastAPI Dependencies

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Get current authenticated user from JWT token."""
    try:
        token = credentials.credentials
        payload = decode_access_token(token)

        # Check if the token is blacklisted (revoked)
        try:
            if token_blacklist.is_blacklisted(token):
                raise AuthenticationError("Token has been revoked")
        except AuthenticationError:
            raise
        except Exception:
            # If blacklist check fails for any reason, fail-safe to allow auth
            # rather than blocking due to monitoring/backing service issues.
            pass
        
        # Verify user exists and is active
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        
        if not user:
            raise AuthenticationError("User not found or inactive")
        
        return payload
    
    except Exception as e:
        if isinstance(e, (AuthenticationError, AuthorizationError)):
            raise
        raise AuthenticationError()


def require_permission(permission: Permission):
    """Dependency to require specific permission."""
    async def permission_checker(
        current_user: dict = Depends(get_current_user)
    ):
        user_permissions = current_user.get("permissions", [])
        
        if not rbac.check_permission(user_permissions, permission):
            raise AuthorizationError(f"Permission denied: {permission.value}")
        
        return current_user
    
    return permission_checker


def require_any_permission(*permissions: Permission):
    """Dependency to require any of the specified permissions."""
    async def permission_checker(
        current_user: dict = Depends(get_current_user)
    ):
        user_permissions = current_user.get("permissions", [])
        
        for permission in permissions:
            if rbac.check_permission(user_permissions, permission):
                return current_user
        
        raise AuthorizationError("Insufficient permissions")
    
    return permission_checker


def require_role(*roles: str):
    """Dependency to require specific role(s)."""
    async def role_checker(
        current_user: dict = Depends(get_current_user)
    ):
        user_roles = current_user.get("roles", [])
        
        for role in roles:
            if role in user_roles:
                return current_user
        
        raise AuthorizationError("Insufficient role")
    
    return role_checker


# User Authentication

def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """Authenticate user with username and password."""
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


def initialize_roles(db: Session):
    """Initialize default roles in database."""
    for role_name, permissions in rbac.role_permissions.items():
        existing_role = db.query(Role).filter(Role.name == role_name).first()
        
        if not existing_role:
            role = Role(
                id=f"role_{role_name}",
                name=role_name,
                description=f"Default {role_name} role",
                permissions=[p.value if isinstance(p, Permission) else p for p in permissions]
            )
            db.add(role)
    
    db.commit()
    print("Default roles initialized")


def create_default_admin(db: Session, username: str = "admin", password: str = "admin123", email: str = "admin@event.local"):
    """Create default admin user."""
    # Check if admin exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"User {username} already exists")
        return existing_user
    
    # Create admin user
    user = User(
        id=f"user_{secrets.token_hex(8)}",
        username=username,
        email=email,
        password_hash=hash_password(password),
        full_name="System Administrator",
        is_active=True,
        is_verified=True,
        consent_data_processing=True
    )
    
    # Assign admin role
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if admin_role:
        user.roles.append(admin_role)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"Default admin user created: {username} / {password}")
    print("⚠️  CHANGE THE DEFAULT PASSWORD IMMEDIATELY!")
    
    return user
