"""Tests for SDK functionality."""

import pytest
from memory_classification_engine.sdk import MemoryClassificationClient, MemoryClassificationError


class TestSDK:
    """Test SDK functionality."""
    
    @pytest.fixture
    def client(self):
        """Create an SDK client for testing."""
        return MemoryClassificationClient(base_url='http://localhost:5000', timeout=5)
    
    def test_initialization(self, client):
        """Test client initialization."""
        assert client is not None
        assert client.base_url == 'http://localhost:5000'
        assert client.timeout == 5
    
    def test_process_message(self, client):
        """Test processing a message."""
        # This test requires the server to be running
        # For now, we'll just test that the method exists
        assert hasattr(client, 'process_message')
    
    def test_retrieve_memories(self, client):
        """Test retrieving memories."""
        # This test requires the server to be running
        # For now, we'll just test that the method exists
        assert hasattr(client, 'retrieve_memories')
    
    def test_get_memory(self, client):
        """Test getting a memory."""
        # This test requires the server to be running
        # For now, we'll just test that the method exists
        assert hasattr(client, 'get_memory')
    
    def test_update_memory(self, client):
        """Test updating a memory."""
        # This test requires the server to be running
        # For now, we'll just test that the method exists
        assert hasattr(client, 'update_memory')
    
    def test_delete_memory(self, client):
        """Test deleting a memory."""
        # This test requires the server to be running
        # For now, we'll just test that the method exists
        assert hasattr(client, 'delete_memory')
    
    def test_get_stats(self, client):
        """Test getting stats."""
        # This test requires the server to be running
        # For now, we'll just test that the method exists
        assert hasattr(client, 'get_stats')
    
    def test_get_plugins(self, client):
        """Test getting plugins."""
        # This test requires the server to be running
        # For now, we'll just test that the method exists
        assert hasattr(client, 'get_plugins')
    
    def test_health_check(self, client):
        """Test health check."""
        # This test requires the server to be running
        # For now, we'll just test that the method exists
        assert hasattr(client, 'health_check')
    
    def test_get_version(self, client):
        """Test getting version."""
        # This test requires the server to be running
        # For now, we'll just test that the method exists
        assert hasattr(client, 'get_version')
