"""Security utilities for Memory Classification Engine."""

import os
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from memory_classification_engine.utils.logger import logger


class SecurityManager:
    """Security manager for Memory Classification Engine."""
    
    def __init__(self, secret_key: str = None, algorithm: str = 'HS256'):
        """Initialize the security manager.
        
        Args:
            secret_key: Secret key for JWT tokens.
            algorithm: JWT algorithm.
        """
        self.secret_key = secret_key or os.environ.get('SECRET_KEY', secrets.token_hex(32))
        self.algorithm = algorithm
        self.token_expiration = timedelta(hours=24)  # 24 hours
    
    def generate_token(self, user_id: str, role: str = 'user') -> str:
        """Generate a JWT token.
        
        Args:
            user_id: User ID.
            role: User role.
            
        Returns:
            JWT token string.
        """
        try:
            payload = {
                'sub': user_id,
                'role': role,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + self.token_expiration
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Error generating token: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token.
        
        Args:
            token: JWT token string.
            
        Returns:
            Decoded payload or None if invalid.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    def hash_password(self, password: str) -> str:
        """Hash a password.
        
        Args:
            password: Plain text password.
            
        Returns:
            Hashed password.
        """
        try:
            # Use bcrypt in a real implementation
            # For now, use a simple hashing for demonstration
            salt = secrets.token_hex(16)
            hashed = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return f"{salt}:{hashed.hex()}"
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against a hash.
        
        Args:
            password: Plain text password.
            hashed_password: Hashed password.
            
        Returns:
            True if password matches, False otherwise.
        """
        try:
            salt, hash_part = hashed_password.split(':')
            hashed = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return hashed.hex() == hash_part
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def generate_api_key(self) -> str:
        """Generate an API key.
        
        Returns:
            API key string.
        """
        return secrets.token_urlsafe(32)
    
    def validate_api_key(self, api_key: str, valid_keys: List[str]) -> bool:
        """Validate an API key.
        
        Args:
            api_key: API key to validate.
            valid_keys: List of valid API keys.
            
        Returns:
            True if API key is valid, False otherwise.
        """
        return api_key in valid_keys
    
    def sanitize_input(self, input_str: str) -> str:
        """Sanitize input to prevent injection attacks.
        
        Args:
            input_str: Input string to sanitize.
            
        Returns:
            Sanitized input string.
        """
        # Basic sanitization
        return input_str.replace('\'', '\\\'').replace('"', '\\"')
    
    def validate_input(self, input_str: str, max_length: int = 1000) -> bool:
        """Validate input.
        
        Args:
            input_str: Input string to validate.
            max_length: Maximum length of input.
            
        Returns:
            True if input is valid, False otherwise.
        """
        if not input_str:
            return False
        if len(input_str) > max_length:
            return False
        return True


class AuthorizationManager:
    """Authorization manager for Memory Classification Engine."""
    
    def __init__(self):
        """Initialize the authorization manager."""
        self.permissions = {
            'admin': ['read', 'write', 'delete', 'admin'],
            'user': ['read', 'write'],
            'guest': ['read']
        }
    
    def has_permission(self, role: str, permission: str) -> bool:
        """Check if a role has a permission.
        
        Args:
            role: User role.
            permission: Permission to check.
            
        Returns:
            True if role has permission, False otherwise.
        """
        if role not in self.permissions:
            return False
        return permission in self.permissions[role]
    
    def get_permissions(self, role: str) -> List[str]:
        """Get permissions for a role.
        
        Args:
            role: User role.
            
        Returns:
            List of permissions.
        """
        return self.permissions.get(role, [])
    
    def add_role(self, role: str, permissions: List[str]):
        """Add a new role with permissions.
        
        Args:
            role: Role name.
            permissions: List of permissions.
        """
        self.permissions[role] = permissions
    
    def update_role(self, role: str, permissions: List[str]):
        """Update permissions for a role.
        
        Args:
            role: Role name.
            permissions: List of permissions.
        """
        if role in self.permissions:
            self.permissions[role] = permissions
    
    def remove_role(self, role: str):
        """Remove a role.
        
        Args:
            role: Role name.
        """
        if role in self.permissions:
            del self.permissions[role]


# Global security instances
security_manager = SecurityManager()
authorization_manager = AuthorizationManager()
