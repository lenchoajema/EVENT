# Appendix D: Security Plan
## Coordinated Satellite & UAV Event-Analysis MVP

**Document Version:** 1.0  
**Date:** November 9, 2025  
**Parent Document:** [API & Message Protocols (Appendix C)](./APPENDIX_C_API_PROTOCOLS.md)

---

## Appendix D: Security Plan

Comprehensive security architecture, threat model, encryption standards, and compliance framework.

---

### D.1 Threat Model & Attack Surface

#### Attack Surface Analysis

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ATTACK SURFACE COMPONENTS                                               │
├─────────────────────────────────────────────────────────────────────────┤
│ External Attack Vectors                                                  │
│  - API endpoints (REST, WebSocket)                                       │
│  - MQTT broker (port 1883, 8883)                                         │
│  - Dashboard web interface (port 3000)                                   │
│  - MinIO storage (port 9000, 9001)                                       │
│  - Database (PostgreSQL port 5432)                                       │
│  - UAV communication channels                                            │
│  - Satellite data feeds                                                  │
│                                                                          │
│ Internal Attack Vectors                                                  │
│  - Container escape vulnerabilities                                      │
│  - Inter-service communication                                           │
│  - Privilege escalation                                                  │
│  - Data exfiltration                                                     │
│  - Supply chain attacks                                                  │
│                                                                          │
│ Physical Attack Vectors                                                  │
│  - UAV hijacking/jamming                                                 │
│  - GPS spoofing                                                          │
│  - Physical access to ground station                                     │
│  - Hardware tampering                                                    │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Threat Classification

| Threat ID | Threat Type | Impact | Likelihood | Risk Level |
|-----------|-------------|--------|------------|------------|
| T-01 | Unauthorized API access | High | Medium | **HIGH** |
| T-02 | Data interception (MITM) | Critical | Medium | **CRITICAL** |
| T-03 | UAV hijacking | Critical | Low | **MEDIUM** |
| T-04 | GPS spoofing | High | Medium | **HIGH** |
| T-05 | Database breach | Critical | Low | **MEDIUM** |
| T-06 | DDoS attack | Medium | High | **MEDIUM** |
| T-07 | Malicious detection injection | High | Low | **MEDIUM** |
| T-08 | Model poisoning | Critical | Very Low | **LOW** |
| T-09 | Insider threat | High | Low | **MEDIUM** |
| T-10 | Physical UAV capture | Medium | Low | **LOW** |

#### Attack Scenarios

**Scenario 1: API Authentication Bypass**
```
Attacker Goal: Gain unauthorized access to system APIs
Attack Vector: Exploit JWT token vulnerabilities
Potential Impact: 
  - Unauthorized data access
  - False alert injection
  - Mission manipulation
Mitigation:
  - Short-lived tokens (15 min)
  - Refresh token rotation
  - IP whitelisting
  - Rate limiting
  - Anomaly detection
```

**Scenario 2: UAV Command Injection**
```
Attacker Goal: Control UAV through command injection
Attack Vector: Intercept/forge MQTT commands
Potential Impact:
  - Mission disruption
  - UAV crash
  - Privacy violation
  - Data exfiltration
Mitigation:
  - TLS 1.3 encryption
  - Command signing (HMAC-SHA256)
  - Command sequence validation
  - Geofencing enforcement
  - Kill switch mechanism
```

**Scenario 3: Data Exfiltration**
```
Attacker Goal: Steal sensitive detection data
Attack Vector: Database or S3 breach
Potential Impact:
  - Privacy violation
  - Intelligence leakage
  - Regulatory penalties
Mitigation:
  - Data-at-rest encryption (AES-256)
  - Access controls (RBAC)
  - Audit logging
  - Data loss prevention (DLP)
  - Regular backups
```

---

### D.2 Authentication & Authorization

#### Authentication Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ AUTHENTICATION FLOW                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐                     ┌──────────┐                          │
│  │  Client  │                     │   API    │                          │
│  │          │                     │  Server  │                          │
│  └─────┬────┘                     └────┬─────┘                          │
│        │                               │                                │
│        │ 1. POST /auth/login           │                                │
│        │   {username, password}        │                                │
│        │─────────────────────────────>│                                │
│        │                               │                                │
│        │                               │ 2. Validate credentials        │
│        │                               │    (bcrypt hash + salt)        │
│        │                               │                                │
│        │                               │ 3. Check MFA (if enabled)      │
│        │                               │                                │
│        │ 4. Return tokens              │                                │
│        │   {access_token,              │                                │
│        │    refresh_token}             │                                │
│        │<─────────────────────────────│                                │
│        │                               │                                │
│        │ 5. API Request                │                                │
│        │   Authorization:              │                                │
│        │   Bearer <access_token>       │                                │
│        │─────────────────────────────>│                                │
│        │                               │                                │
│        │                               │ 6. Validate JWT               │
│        │                               │    - Signature                │
│        │                               │    - Expiry                   │
│        │                               │    - Issuer                   │
│        │                               │    - Claims                   │
│        │                               │                                │
│        │ 7. Response                   │                                │
│        │<─────────────────────────────│                                │
│        │                               │                                │
└─────────────────────────────────────────────────────────────────────────┘
```

#### JWT Token Structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "event-key-2025-11"
  },
  "payload": {
    "sub": "user_12345",
    "username": "operator_john",
    "email": "john@event-system.com",
    "roles": ["operator", "viewer"],
    "permissions": [
      "detections:read",
      "alerts:read",
      "alerts:acknowledge",
      "missions:read",
      "missions:create",
      "uavs:read"
    ],
    "iat": 1699545600,
    "exp": 1699546500,
    "iss": "event-auth-server",
    "aud": "event-api"
  },
  "signature": "RSASHA256(...)"
}
```

#### Role-Based Access Control (RBAC)

```python
from enum import Enum
from typing import List, Set
from dataclasses import dataclass

class Permission(str, Enum):
    """System permissions."""
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
    
    # System
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"
    USERS_MANAGE = "users:manage"

@dataclass
class Role:
    """User role with permissions."""
    name: str
    permissions: Set[Permission]
    description: str

class RBACManager:
    """Role-Based Access Control manager."""
    
    def __init__(self):
        self.roles = self._initialize_roles()
    
    def _initialize_roles(self) -> dict:
        """Initialize default roles."""
        return {
            "viewer": Role(
                name="viewer",
                permissions={
                    Permission.DETECTIONS_READ,
                    Permission.ALERTS_READ,
                    Permission.MISSIONS_READ,
                    Permission.UAVS_READ
                },
                description="Read-only access to system data"
            ),
            "operator": Role(
                name="operator",
                permissions={
                    Permission.DETECTIONS_READ,
                    Permission.DETECTIONS_CREATE,
                    Permission.ALERTS_READ,
                    Permission.ALERTS_ACKNOWLEDGE,
                    Permission.ALERTS_DISMISS,
                    Permission.MISSIONS_READ,
                    Permission.MISSIONS_CREATE,
                    Permission.MISSIONS_UPDATE,
                    Permission.UAVS_READ,
                    Permission.UAVS_COMMAND
                },
                description="Operational control of UAVs and missions"
            ),
            "supervisor": Role(
                name="supervisor",
                permissions={
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
                    Permission.SYSTEM_CONFIG
                },
                description="Full operational control plus configuration"
            ),
            "admin": Role(
                name="admin",
                permissions=set(Permission),  # All permissions
                description="Full system access"
            )
        }
    
    def check_permission(self, user_roles: List[str], required_permission: Permission) -> bool:
        """Check if user has required permission."""
        for role_name in user_roles:
            role = self.roles.get(role_name)
            if role and required_permission in role.permissions:
                return True
        return False
    
    def get_user_permissions(self, user_roles: List[str]) -> Set[Permission]:
        """Get all permissions for user roles."""
        permissions = set()
        for role_name in user_roles:
            role = self.roles.get(role_name)
            if role:
                permissions.update(role.permissions)
        return permissions

# FastAPI dependency for permission checking
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()
rbac = RBACManager()

async def require_permission(permission: Permission):
    """Dependency to require specific permission."""
    async def permission_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        try:
            # Decode JWT
            token = credentials.credentials
            payload = jwt.decode(
                token,
                PUBLIC_KEY,
                algorithms=["RS256"],
                audience="event-api"
            )
            
            # Extract roles
            user_roles = payload.get("roles", [])
            
            # Check permission
            if not rbac.check_permission(user_roles, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value}"
                )
            
            return payload
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    return permission_checker

# Usage in FastAPI endpoints
from fastapi import APIRouter

router = APIRouter()

@router.post("/missions")
async def create_mission(
    mission_data: dict,
    user = Depends(require_permission(Permission.MISSIONS_CREATE))
):
    """Create new mission (requires missions:create permission)."""
    # Mission creation logic
    pass

@router.post("/uavs/{uav_id}/command")
async def send_uav_command(
    uav_id: str,
    command: dict,
    user = Depends(require_permission(Permission.UAVS_COMMAND))
):
    """Send command to UAV (requires uavs:command permission)."""
    # Command logic
    pass
```

#### Multi-Factor Authentication (MFA)

```python
import pyotp
import qrcode
from io import BytesIO
import base64

class MFAManager:
    """Multi-Factor Authentication manager."""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate new MFA secret."""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(username: str, secret: str, issuer: str = "EVENT") -> str:
        """Generate QR code for authenticator app."""
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name=username,
            issuer_name=issuer
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Allow 30s window

# Enable MFA for user
@router.post("/auth/mfa/enable")
async def enable_mfa(user = Depends(get_current_user)):
    """Enable MFA for user."""
    secret = MFAManager.generate_secret()
    qr_code = MFAManager.generate_qr_code(user.username, secret)
    
    # Store secret (encrypted) in database
    user.mfa_secret = encrypt_secret(secret)
    user.mfa_enabled = False  # Set to True after verification
    db.commit()
    
    return {
        "secret": secret,
        "qr_code": qr_code
    }

@router.post("/auth/mfa/verify")
async def verify_mfa(token: str, user = Depends(get_current_user)):
    """Verify MFA token and complete setup."""
    secret = decrypt_secret(user.mfa_secret)
    
    if MFAManager.verify_totp(secret, token):
        user.mfa_enabled = True
        db.commit()
        return {"message": "MFA enabled successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid token")
```

---

### D.3 Encryption Standards

#### Encryption At-Rest

```
┌─────────────────────────────────────────────────────────────────────────┐
│ DATA-AT-REST ENCRYPTION                                                 │
├─────────────────────────────────────────────────────────────────────────┤
│ Database (PostgreSQL)                                                    │
│  - Algorithm: AES-256-GCM                                                │
│  - Key Management: AWS KMS / HashiCorp Vault                             │
│  - Tablespace Encryption: Enabled                                        │
│  - Backup Encryption: AES-256                                            │
│                                                                          │
│ Object Storage (MinIO/S3)                                                │
│  - Algorithm: AES-256-CBC                                                │
│  - Server-Side Encryption (SSE): Enabled                                 │
│  - Bucket Encryption: Default enabled                                    │
│  - Client-Side Encryption: Optional                                      │
│                                                                          │
│ Container Volumes                                                        │
│  - LUKS encryption on host volumes                                       │
│  - dm-crypt for sensitive data                                           │
│                                                                          │
│ Secrets                                                                  │
│  - Docker secrets: encrypted swarm mode                                  │
│  - Kubernetes secrets: encrypted etcd                                    │
│  - Environment variables: Vault-injected                                 │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Encryption In-Transit

```
┌─────────────────────────────────────────────────────────────────────────┐
│ DATA-IN-TRANSIT ENCRYPTION                                              │
├─────────────────────────────────────────────────────────────────────────┤
│ HTTPS/TLS                                                                │
│  - Protocol: TLS 1.3 (minimum TLS 1.2)                                   │
│  - Cipher Suites:                                                        │
│    * TLS_AES_256_GCM_SHA384                                              │
│    * TLS_CHACHA20_POLY1305_SHA256                                        │
│    * TLS_AES_128_GCM_SHA256                                              │
│  - Certificate: Let's Encrypt / DigiCert                                 │
│  - HSTS: Enabled (max-age=31536000)                                      │
│                                                                          │
│ MQTT/TLS                                                                 │
│  - Port: 8883 (TLS enabled)                                              │
│  - Protocol: TLS 1.3                                                     │
│  - Client Certificates: Required for UAVs                                │
│  - CA: Internal PKI                                                      │
│                                                                          │
│ WebSocket Secure (WSS)                                                   │
│  - Protocol: WSS over TLS 1.3                                            │
│  - Port: 443                                                             │
│  - Same cipher suites as HTTPS                                           │
│                                                                          │
│ Database Connections                                                     │
│  - PostgreSQL: SSL mode 'require'                                        │
│  - Certificate verification: Enabled                                     │
│  - Redis: TLS enabled (port 6380)                                        │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Key Management

```python
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import bytes

class KeyManager:
    """Encryption key management."""
    
    def __init__(self, kms_backend: str = "vault"):
        """
        Initialize key manager.
        
        Args:
            kms_backend: 'vault', 'aws_kms', or 'local'
        """
        self.kms_backend = kms_backend
        self.master_key = self._load_master_key()
    
    def _load_master_key(self) -> bytes:
        """Load master encryption key from KMS."""
        if self.kms_backend == "vault":
            return self._load_from_vault()
        elif self.kms_backend == "aws_kms":
            return self._load_from_aws_kms()
        else:
            # Local development only
            key = os.environ.get("MASTER_KEY")
            if not key:
                raise ValueError("MASTER_KEY environment variable not set")
            return key.encode()
    
    def _load_from_vault(self) -> bytes:
        """Load key from HashiCorp Vault."""
        import hvac
        client = hvac.Client(url=os.environ["VAULT_ADDR"])
        client.token = os.environ["VAULT_TOKEN"]
        
        secret = client.secrets.kv.v2.read_secret_version(
            path="event/encryption-key"
        )
        return secret["data"]["data"]["key"].encode()
    
    def _load_from_aws_kms(self) -> bytes:
        """Load key from AWS KMS."""
        import boto3
        kms = boto3.client("kms")
        
        # Generate data key
        response = kms.generate_data_key(
            KeyId=os.environ["AWS_KMS_KEY_ID"],
            KeySpec="AES_256"
        )
        return response["Plaintext"]
    
    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt a database field."""
        f = Fernet(self.master_key)
        encrypted = f.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt_field(self, ciphertext: str) -> str:
        """Decrypt a database field."""
        f = Fernet(self.master_key)
        decrypted = f.decrypt(ciphertext.encode())
        return decrypted.decode()
    
    def encrypt_file(self, file_path: str, output_path: str):
        """Encrypt a file using AES-256-GCM."""
        # Generate random key and nonce
        key = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        
        # Read file
        with open(file_path, "rb") as f:
            plaintext = f.read()
        
        # Encrypt
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        # Write encrypted file (nonce + ciphertext)
        with open(output_path, "wb") as f:
            f.write(nonce + ciphertext)
        
        # Store key securely (e.g., in KMS)
        self._store_file_key(output_path, key)
    
    def decrypt_file(self, encrypted_path: str, output_path: str):
        """Decrypt a file."""
        # Retrieve key from KMS
        key = self._retrieve_file_key(encrypted_path)
        aesgcm = AESGCM(key)
        
        # Read encrypted file
        with open(encrypted_path, "rb") as f:
            data = f.read()
        
        # Extract nonce and ciphertext
        nonce = data[:12]
        ciphertext = data[12:]
        
        # Decrypt
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        # Write decrypted file
        with open(output_path, "wb") as f:
            f.write(plaintext)

# Database model with encrypted fields
from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
key_manager = KeyManager()

class EncryptedUser(Base):
    """User model with encrypted sensitive fields."""
    __tablename__ = "users_encrypted"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    _mfa_secret = Column("mfa_secret", Text)  # Encrypted
    _api_key = Column("api_key", Text)  # Encrypted
    
    @property
    def mfa_secret(self) -> str:
        """Decrypt MFA secret."""
        if self._mfa_secret:
            return key_manager.decrypt_field(self._mfa_secret)
        return None
    
    @mfa_secret.setter
    def mfa_secret(self, value: str):
        """Encrypt MFA secret."""
        if value:
            self._mfa_secret = key_manager.encrypt_field(value)
        else:
            self._mfa_secret = None
    
    @property
    def api_key(self) -> str:
        """Decrypt API key."""
        if self._api_key:
            return key_manager.decrypt_field(self._api_key)
        return None
    
    @api_key.setter
    def api_key(self, value: str):
        """Encrypt API key."""
        if value:
            self._api_key = key_manager.encrypt_field(value)
        else:
            self._api_key = None
```

---

### D.4 Audit Logging & Monitoring

#### Audit Log Schema

```python
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Enum as SQLEnum
from enum import Enum

class AuditAction(str, Enum):
    """Audit action types."""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    COMMAND = "command"
    CONFIG_CHANGE = "config_change"
    ALERT_ACK = "alert_acknowledge"
    MISSION_START = "mission_start"
    MISSION_ABORT = "mission_abort"

class AuditLog(Base):
    """Audit log entry."""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String, index=True)
    username = Column(String)
    action = Column(SQLEnum(AuditAction), index=True)
    resource_type = Column(String, index=True)
    resource_id = Column(String)
    ip_address = Column(String)
    user_agent = Column(String)
    status = Column(String)  # success, failure
    details = Column(JSON)
    request_id = Column(String, index=True)

class AuditLogger:
    """Audit logging utility."""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def log(
        self,
        user_id: str,
        username: str,
        action: AuditAction,
        resource_type: str,
        resource_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        status: str = "success",
        details: dict = None
    ):
        """Log an audit event."""
        log_entry = AuditLog(
            id=f"audit_{int(datetime.utcnow().timestamp() * 1000)}",
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            details=details or {}
        )
        
        self.db.add(log_entry)
        self.db.commit()
        
        # Also log to SIEM (Security Information and Event Management)
        self._send_to_siem(log_entry)
    
    def _send_to_siem(self, log_entry: AuditLog):
        """Send audit log to SIEM system."""
        # Implementation depends on SIEM (Splunk, ELK, etc.)
        pass

# FastAPI middleware for audit logging
from fastapi import Request
import uuid

@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    """Audit logging middleware."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Log request
    start_time = datetime.utcnow()
    
    try:
        response = await call_next(request)
        
        # Log successful request
        if hasattr(request.state, "user"):
            audit_logger.log(
                user_id=request.state.user.get("sub"),
                username=request.state.user.get("username"),
                action=AuditAction.READ,  # Determine from method/path
                resource_type=request.url.path.split("/")[2] if len(request.url.path.split("/")) > 2 else "unknown",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                status="success",
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                    "request_id": request_id
                }
            )
        
        return response
    
    except Exception as e:
        # Log failed request
        if hasattr(request.state, "user"):
            audit_logger.log(
                user_id=request.state.user.get("sub"),
                username=request.state.user.get("username"),
                action=AuditAction.READ,
                resource_type=request.url.path.split("/")[2] if len(request.url.path.split("/")) > 2 else "unknown",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                status="failure",
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "request_id": request_id
                }
            )
        raise
```

#### Security Monitoring

```python
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List

class SecurityMonitor:
    """Real-time security monitoring."""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
        self.failed_login_attempts = defaultdict(list)
        self.rate_limit_violations = defaultdict(list)
        self.anomaly_scores = {}
    
    def track_failed_login(self, username: str, ip_address: str):
        """Track failed login attempt."""
        self.failed_login_attempts[username].append({
            "timestamp": datetime.utcnow(),
            "ip_address": ip_address
        })
        
        # Check for brute force attack
        recent_failures = [
            f for f in self.failed_login_attempts[username]
            if f["timestamp"] > datetime.utcnow() - timedelta(minutes=15)
        ]
        
        if len(recent_failures) >= 5:
            self.alert_brute_force(username, ip_address, len(recent_failures))
    
    def alert_brute_force(self, username: str, ip_address: str, attempts: int):
        """Alert on potential brute force attack."""
        self.logger.warning(
            f"SECURITY ALERT: Brute force detected - "
            f"Username: {username}, IP: {ip_address}, Attempts: {attempts}"
        )
        
        # Take action
        self.block_ip(ip_address)
        self.notify_security_team({
            "alert_type": "brute_force",
            "username": username,
            "ip_address": ip_address,
            "attempts": attempts
        })
    
    def detect_anomalies(self, user_id: str, action: str, context: dict):
        """Detect anomalous behavior."""
        # Example: User accessing resources at unusual times
        current_hour = datetime.utcnow().hour
        
        # Check if outside normal hours (9 AM - 5 PM)
        if current_hour < 9 or current_hour > 17:
            self.logger.warning(
                f"ANOMALY: User {user_id} accessing {action} at unusual time: {current_hour}:00"
            )
            self.anomaly_scores[user_id] = self.anomaly_scores.get(user_id, 0) + 1
        
        # Check for rapid succession of actions
        if self.check_rapid_actions(user_id):
            self.logger.warning(
                f"ANOMALY: User {user_id} performing rapid actions"
            )
            self.anomaly_scores[user_id] = self.anomaly_scores.get(user_id, 0) + 2
        
        # Alert if anomaly score exceeds threshold
        if self.anomaly_scores.get(user_id, 0) >= 5:
            self.alert_suspicious_activity(user_id)
    
    def check_rapid_actions(self, user_id: str, window_seconds: int = 60, threshold: int = 50) -> bool:
        """Check if user is performing actions too rapidly."""
        # Query recent actions from audit log
        recent_actions = self.get_recent_actions(user_id, window_seconds)
        return len(recent_actions) > threshold
    
    def block_ip(self, ip_address: str, duration_minutes: int = 60):
        """Block IP address."""
        # Add to firewall/iptables
        self.logger.info(f"Blocking IP {ip_address} for {duration_minutes} minutes")
        # Implementation: Update firewall rules
    
    def notify_security_team(self, alert: dict):
        """Notify security team of incident."""
        # Send to Slack/PagerDuty/Email
        self.logger.critical(f"Security incident: {alert}")

# Integration with FastAPI
security_monitor = SecurityMonitor()

@router.post("/auth/login")
async def login(credentials: LoginCredentials, request: Request):
    """Login endpoint with security monitoring."""
    try:
        user = authenticate_user(credentials.username, credentials.password)
        
        if not user:
            # Track failed login
            security_monitor.track_failed_login(
                credentials.username,
                request.client.host
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate tokens
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
        
        # Audit log
        audit_logger.log(
            user_id=user.id,
            username=user.username,
            action=AuditAction.LOGIN,
            resource_type="auth",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            status="success"
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    except Exception as e:
        security_monitor.track_failed_login(
            credentials.username,
            request.client.host
        )
        raise
```

---

### D.5 Network Security

#### Firewall Configuration

```bash
#!/bin/bash
# Firewall rules for EVENT system

# Flush existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

# Default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH (restrict to management network)
iptables -A INPUT -p tcp --dport 22 -s 10.0.0.0/24 -j ACCEPT

# Allow HTTPS (public API)
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow MQTT over TLS (UAV connections)
iptables -A INPUT -p tcp --dport 8883 -s 10.0.1.0/24 -j ACCEPT

# Block common attack ports
iptables -A INPUT -p tcp --dport 23 -j DROP  # Telnet
iptables -A INPUT -p tcp --dport 135 -j DROP # Windows RPC
iptables -A INPUT -p tcp --dport 139 -j DROP # NetBIOS
iptables -A INPUT -p tcp --dport 445 -j DROP # SMB

# Rate limiting (DDoS protection)
iptables -A INPUT -p tcp --dport 443 -m limit --limit 100/minute --limit-burst 200 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j DROP

# Log dropped packets
iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables-dropped: " --log-level 7

# Save rules
iptables-save > /etc/iptables/rules.v4
```

#### VPN Configuration (WireGuard)

```ini
# /etc/wireguard/wg0.conf
[Interface]
Address = 10.0.2.1/24
ListenPort = 51820
PrivateKey = <SERVER_PRIVATE_KEY>
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# UAV Client 1
[Peer]
PublicKey = <UAV_001_PUBLIC_KEY>
AllowedIPs = 10.0.2.101/32

# UAV Client 2
[Peer]
PublicKey = <UAV_002_PUBLIC_KEY>
AllowedIPs = 10.0.2.102/32

# Admin Client
[Peer]
PublicKey = <ADMIN_PUBLIC_KEY>
AllowedIPs = 10.0.2.200/32
```

---

### D.6 Compliance & Regulations

#### GDPR Compliance

```python
from datetime import datetime, timedelta
from typing import List

class GDPRCompliance:
    """GDPR compliance utilities."""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def export_user_data(self, user_id: str) -> dict:
        """Export all user data (GDPR Article 20)."""
        user = self.db.query(User).filter_by(id=user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        return {
            "personal_data": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            },
            "activity_logs": self.get_user_audit_logs(user_id),
            "missions_created": self.get_user_missions(user_id),
            "alerts_acknowledged": self.get_user_alerts(user_id)
        }
    
    def delete_user_data(self, user_id: str):
        """Delete all user data (GDPR Article 17 - Right to be forgotten)."""
        # Anonymize audit logs (retain for legal purposes)
        self.db.query(AuditLog).filter_by(user_id=user_id).update({
            "username": "DELETED_USER",
            "details": None
        })
        
        # Delete personal data
        user = self.db.query(User).filter_by(id=user_id).first()
        if user:
            self.db.delete(user)
        
        self.db.commit()
    
    def apply_data_retention(self):
        """Apply data retention policies."""
        # Delete old audit logs (retain for 2 years)
        retention_date = datetime.utcnow() - timedelta(days=730)
        self.db.query(AuditLog).filter(
            AuditLog.timestamp < retention_date
        ).delete()
        
        # Archive old detections (retain active for 90 days)
        archive_date = datetime.utcnow() - timedelta(days=90)
        old_detections = self.db.query(Detection).filter(
            Detection.timestamp < archive_date
        ).all()
        
        for detection in old_detections:
            self.archive_detection(detection)
            self.db.delete(detection)
        
        self.db.commit()
    
    def get_consent_status(self, user_id: str) -> dict:
        """Get user consent status."""
        user = self.db.query(User).filter_by(id=user_id).first()
        
        return {
            "data_processing": user.consent_data_processing,
            "analytics": user.consent_analytics,
            "third_party_sharing": user.consent_third_party,
            "marketing": user.consent_marketing,
            "last_updated": user.consent_updated_at.isoformat()
        }
```

#### Data Protection Impact Assessment (DPIA)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ DATA PROTECTION IMPACT ASSESSMENT                                       │
├─────────────────────────────────────────────────────────────────────────┤
│ Processing Activity: UAV-based surveillance for event detection         │
│                                                                          │
│ Data Categories:                                                         │
│  - Location data (GPS coordinates)                                       │
│  - Image/video data (potentially including persons)                     │
│  - Operator credentials and access logs                                  │
│  - System telemetry and performance data                                 │
│                                                                          │
│ Legal Basis: Legitimate interest (public safety)                         │
│                                                                          │
│ Privacy Risks:                                                           │
│  1. Unauthorized surveillance of individuals                             │
│     Mitigation: Geofencing, access controls, audit logging               │
│                                                                          │
│  2. Data breach exposing sensitive imagery                               │
│     Mitigation: Encryption (AES-256), access controls, DLP               │
│                                                                          │
│  3. Misuse of detection data                                             │
│     Mitigation: RBAC, purpose limitation, audit trails                   │
│                                                                          │
│  4. Retention of unnecessary personal data                               │
│     Mitigation: Automated data retention policies (90 days)              │
│                                                                          │
│ Data Subject Rights:                                                     │
│  - Right to access (Article 15): Data export functionality               │
│  - Right to erasure (Article 17): Data deletion functionality            │
│  - Right to object (Article 21): Opt-out mechanisms                      │
│                                                                          │
│ Assessment Date: November 9, 2025                                        │
│ Review Date: November 9, 2026                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways

✅ **Threat Model**: 10 identified threats, risk-based mitigation strategies  
✅ **Authentication**: JWT tokens, MFA, OAuth 2.0, 15-min expiry  
✅ **Authorization**: RBAC with 4 roles (viewer, operator, supervisor, admin)  
✅ **Encryption**: AES-256 at-rest, TLS 1.3 in-transit  
✅ **Key Management**: HashiCorp Vault / AWS KMS integration  
✅ **Audit Logging**: Comprehensive logging with SIEM integration  
✅ **Network Security**: Firewall rules, VPN (WireGuard), rate limiting  
✅ **Compliance**: GDPR-compliant (data export, deletion, retention)  

---

## Navigation

- **Previous:** [API & Message Protocols (Appendix C)](./APPENDIX_C_API_PROTOCOLS.md)
- **Home:** [Documentation Index](./README.md)

---

**Document Status:** ✅ Complete  
**Last Updated:** November 9, 2025  
**Review Cycle:** Quarterly  
**Classification:** CONFIDENTIAL
