"""
Security Utilities for Audit Logging, Encryption, and Monitoring.

Implements security features from Appendix D: Security Plan.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from collections import defaultdict
import logging
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .auth_models import AuditLog

logger = logging.getLogger("security")


# ============================================================
# Audit Logging
# ============================================================

class AuditLogger:
    """Audit logging utility."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def log(
        self,
        user_id: str,
        username: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
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
            details=details or {},
            request_id=request_id
        )
        
        try:
            self.db.add(log_entry)
            self.db.commit()
            
            # Log to application log as well
            logger.info(
                f"AUDIT: {username} ({user_id}) - {action} on {resource_type} "
                f"[{resource_id}] - {status}"
            )
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            self.db.rollback()
    
    def log_login(self, user_id: str, username: str, ip_address: str, user_agent: str, success: bool):
        """Log login attempt."""
        self.log(
            user_id=user_id or "unknown",
            username=username,
            action="login",
            resource_type="auth",
            ip_address=ip_address,
            user_agent=user_agent,
            status="success" if success else "failure"
        )
    
    def log_logout(self, user_id: str, username: str, ip_address: str):
        """Log logout."""
        self.log(
            user_id=user_id,
            username=username,
            action="logout",
            resource_type="auth",
            ip_address=ip_address,
            status="success"
        )
    
    def log_permission_denied(self, user_id: str, username: str, resource_type: str, resource_id: str):
        """Log permission denied attempt."""
        self.log(
            user_id=user_id,
            username=username,
            action="access_denied",
            resource_type=resource_type,
            resource_id=resource_id,
            status="failure",
            details={"reason": "insufficient_permissions"}
        )


# ============================================================
# Security Monitoring
# ============================================================

class SecurityMonitor:
    """Real-time security monitoring."""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
        self.failed_login_attempts = defaultdict(list)
        self.rate_limit_violations = defaultdict(list)
        self.anomaly_scores = {}
        self.blocked_ips = set()
    
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
        
        # Block IP
        self.block_ip(ip_address)
        
        # TODO: Send notification to security team
    
    def block_ip(self, ip_address: str, duration_minutes: int = 60):
        """Block IP address."""
        self.blocked_ips.add(ip_address)
        self.logger.info(f"Blocked IP {ip_address} for {duration_minutes} minutes")
        
        # TODO: Update firewall rules or rate limiter
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked."""
        return ip_address in self.blocked_ips
    
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
        
        # Alert if anomaly score exceeds threshold
        if self.anomaly_scores.get(user_id, 0) >= 5:
            self.alert_suspicious_activity(user_id)
    
    def alert_suspicious_activity(self, user_id: str):
        """Alert on suspicious activity."""
        self.logger.critical(f"SECURITY ALERT: Suspicious activity from user {user_id}")
        
        # TODO: Send notification and possibly suspend account
    
    def get_statistics(self) -> dict:
        """Get security monitoring statistics."""
        return {
            "blocked_ips": len(self.blocked_ips),
            "failed_login_accounts": len(self.failed_login_attempts),
            "high_anomaly_users": len([
                user_id for user_id, score in self.anomaly_scores.items()
                if score >= 3
            ])
        }


# Global security monitor instance
security_monitor = SecurityMonitor()


# ============================================================
# Encryption Utilities
# ============================================================

class KeyManager:
    """Encryption key management."""
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize key manager.
        
        Args:
            master_key: Master encryption key. If None, loads from environment.
        """
        if master_key:
            self.master_key = master_key
        else:
            # Load from environment or generate for development
            key_str = os.environ.get("ENCRYPTION_KEY")
            if key_str:
                self.master_key = key_str.encode()
            else:
                # Generate new key for development (should use KMS in production)
                self.master_key = Fernet.generate_key()
                logger.warning("Generated new encryption key - NOT SUITABLE FOR PRODUCTION")
        
        self.fernet = Fernet(self.master_key)
    
    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt a database field."""
        if not plaintext:
            return ""
        encrypted = self.fernet.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt_field(self, ciphertext: str) -> str:
        """Decrypt a database field."""
        if not ciphertext:
            return ""
        try:
            decrypted = self.fernet.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return ""
    
    def encrypt_file(self, file_path: str, output_path: str) -> str:
        """
        Encrypt a file using AES-256-GCM.
        
        Returns the key identifier for retrieving the key later.
        """
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
        
        # Generate key ID
        key_id = secrets.token_hex(16)
        
        # TODO: Store key securely (e.g., in KMS or Vault)
        # For now, store in memory (NOT PRODUCTION SAFE)
        if not hasattr(self, '_file_keys'):
            self._file_keys = {}
        self._file_keys[key_id] = key
        
        return key_id
    
    def decrypt_file(self, encrypted_path: str, output_path: str, key_id: str):
        """Decrypt a file."""
        # TODO: Retrieve key from KMS or Vault
        if not hasattr(self, '_file_keys') or key_id not in self._file_keys:
            raise ValueError(f"Key {key_id} not found")
        
        key = self._file_keys[key_id]
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
    
    def hash_sensitive_data(self, data: str) -> str:
        """Create one-way hash of sensitive data."""
        return hashlib.sha256(data.encode()).hexdigest()


# Global key manager instance
key_manager = KeyManager()


# ============================================================
# GDPR Compliance Utilities
# ============================================================

class GDPRCompliance:
    """GDPR compliance utilities."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def export_user_data(self, user_id: str) -> dict:
        """Export all user data (GDPR Article 20)."""
        from .auth_models import User
        
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Collect audit logs
        audit_logs = self.db.query(AuditLog).filter(AuditLog.user_id == user_id).all()
        
        return {
            "personal_data": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            },
            "activity_logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "status": log.status
                }
                for log in audit_logs
            ]
        }
    
    def delete_user_data(self, user_id: str):
        """Delete all user data (GDPR Article 17 - Right to be forgotten)."""
        from .auth_models import User, RefreshToken
        
        # Anonymize audit logs (retain for legal purposes)
        self.db.query(AuditLog).filter(AuditLog.user_id == user_id).update({
            "username": "DELETED_USER",
            "details": None
        })
        
        # Delete refresh tokens
        self.db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        
        # Delete user
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            self.db.delete(user)
        
        self.db.commit()
        logger.info(f"User {user_id} data deleted (GDPR compliance)")
    
    def apply_data_retention(self):
        """Apply data retention policies."""
        from .models import Detection
        
        # Delete old audit logs (retain for 2 years)
        retention_date = datetime.utcnow() - timedelta(days=730)
        deleted_logs = self.db.query(AuditLog).filter(
            AuditLog.timestamp < retention_date
        ).delete()
        
        # Archive old detections (retain active for 90 days)
        archive_date = datetime.utcnow() - timedelta(days=90)
        old_detections = self.db.query(Detection).filter(
            Detection.created_at < archive_date
        ).all()
        
        # TODO: Archive to cold storage before deleting
        for detection in old_detections:
            self.db.delete(detection)
        
        self.db.commit()
        
        logger.info(
            f"Data retention applied: {deleted_logs} audit logs, "
            f"{len(old_detections)} detections archived"
        )


# ============================================================
# Password Policy
# ============================================================

class PasswordPolicy:
    """Password strength validation."""
    
    @staticmethod
    def validate(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength.
        
        Returns (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        # Check for common passwords
        common_passwords = ["password", "12345678", "qwerty", "admin123"]
        if password.lower() in common_passwords:
            return False, "Password is too common"
        
        return True, None
