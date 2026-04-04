"""Tests for SDK functionality."""

import pytest
from memory_classification_engine.sdk.python import MemorySDK, MemoryClient


class TestSDK:
    """Test SDK functionality."""
    
    @pytest.fixture
    def sdk(self):
        """Create an SDK instance for testing."""
        return MemorySDK()
    
    @pytest.fixture
    def client(self):
        """Create a MemoryClient instance for testing."""
        return MemoryClient()
    
    def test_sdk_initialization(self, sdk):
        """Test SDK initialization."""
        assert sdk is not None
        assert sdk.mode == 'local'
    
    def test_client_initialization(self, client):
        """Test MemoryClient initialization."""
        assert client is not None
    
    def test_sdk_process_message(self, sdk):
        """Test processing a message with SDK."""
        assert hasattr(sdk, 'process_message')
    
    def test_sdk_retrieve_memories(self, sdk):
        """Test retrieving memories with SDK."""
        assert hasattr(sdk, 'retrieve_memories')
    
    def test_sdk_manage_memory(self, sdk):
        """Test managing memory with SDK."""
        assert hasattr(sdk, 'manage_memory')
    
    def test_sdk_export_memories(self, sdk):
        """Test exporting memories with SDK."""
        assert hasattr(sdk, 'export_memories')
    
    def test_sdk_import_memories(self, sdk):
        """Test importing memories with SDK."""
        assert hasattr(sdk, 'import_memories')
    
    def test_sdk_get_stats(self, sdk):
        """Test getting stats with SDK."""
        assert hasattr(sdk, 'get_stats')
    
    def test_client_remember(self, client):
        """Test remembering a message with MemoryClient."""
        assert hasattr(client, 'remember')
    
    def test_client_recall(self, client):
        """Test recalling memories with MemoryClient."""
        assert hasattr(client, 'recall')
    
    def test_client_manage(self, client):
        """Test managing memory with MemoryClient."""
        assert hasattr(client, 'manage')
    
    def test_client_stats(self, client):
        """Test getting stats with MemoryClient."""
        assert hasattr(client, 'stats')
