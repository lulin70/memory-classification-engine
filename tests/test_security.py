"""Tests for security functionality."""

import pytest
from memory_classification_engine.utils.security import security_manager, authorization_manager


class TestSecurityManager:
    """Test security manager functionality."""
    
    def test_generate_token(self):
        """Test token generation."""
        token = security_manager.generate_token('test-user', 'admin')
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token(self):
        """Test token verification."""
        token = security_manager.generate_token('test-user', 'user')
        payload = security_manager.verify_token(token)
        assert payload is not None
        assert payload['sub'] == 'test-user'
        assert payload['role'] == 'user'
    
    def test_verify_invalid_token(self):
        """Test invalid token verification."""
        payload = security_manager.verify_token('invalid-token')
        assert payload is None
    
    def test_hash_password(self):
        """Test password hashing."""
        password = 'test-password'
        hashed = security_manager.hash_password(password)
        assert isinstance(hashed, str)
        assert ':' in hashed
    
    def test_verify_password(self):
        """Test password verification."""
        password = 'test-password'
        hashed = security_manager.hash_password(password)
        assert security_manager.verify_password(password, hashed) is True
        assert security_manager.verify_password('wrong-password', hashed) is False
    
    def test_generate_api_key(self):
        """Test API key generation."""
        api_key = security_manager.generate_api_key()
        assert isinstance(api_key, str)
        assert len(api_key) > 0
    
    def test_validate_api_key(self):
        """Test API key validation."""
        valid_keys = ['key1', 'key2', 'key3']
        assert security_manager.validate_api_key('key1', valid_keys) is True
        assert security_manager.validate_api_key('invalid-key', valid_keys) is False
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        input_str = "O'Reilly's \"Book\""
        sanitized = security_manager.sanitize_input(input_str)
        assert isinstance(sanitized, str)
        assert len(sanitized) > 0
    
    def test_validate_input(self):
        """Test input validation."""
        assert security_manager.validate_input('test') is True
        assert security_manager.validate_input('') is False
        assert security_manager.validate_input('a' * 1001) is False


class TestAuthorizationManager:
    """Test authorization manager functionality."""
    
    def test_has_permission(self):
        """Test permission checking."""
        assert authorization_manager.has_permission('admin', 'admin') is True
        assert authorization_manager.has_permission('user', 'write') is True
        assert authorization_manager.has_permission('guest', 'write') is False
    
    def test_get_permissions(self):
        """Test getting permissions."""
        admin_perms = authorization_manager.get_permissions('admin')
        assert 'admin' in admin_perms
        assert 'read' in admin_perms
        
        user_perms = authorization_manager.get_permissions('user')
        assert 'read' in user_perms
        assert 'write' in user_perms
        
        guest_perms = authorization_manager.get_permissions('guest')
        assert 'read' in guest_perms
        assert len(guest_perms) == 1
    
    def test_add_role(self):
        """Test adding a new role."""
        authorization_manager.add_role('editor', ['read', 'write'])
        assert authorization_manager.has_permission('editor', 'write') is True
    
    def test_update_role(self):
        """Test updating a role."""
        authorization_manager.update_role('guest', ['read', 'write'])
        assert authorization_manager.has_permission('guest', 'write') is True
    
    def test_remove_role(self):
        """Test removing a role."""
        authorization_manager.add_role('temp', ['read'])
        assert 'temp' in authorization_manager.permissions
        authorization_manager.remove_role('temp')
        assert 'temp' not in authorization_manager.permissions
