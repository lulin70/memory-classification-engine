"""Tests for distributed deployment functionality."""

import pytest
import time
from memory_classification_engine.utils.distributed import DistributedManager, DataSynchronizer


class TestDistributedManager:
    """Test distributed manager functionality."""
    
    @pytest.fixture
    def manager(self):
        """Create a distributed manager for testing."""
        return DistributedManager(node_id="test_node_1", port=5001, discovery_interval=5)
    
    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager is not None
        assert manager.node_id == "test_node_1"
        assert manager.port == 5001
    
    def test_get_local_ip(self, manager):
        """Test getting local IP."""
        ip = manager._get_local_ip()
        assert ip is not None
        assert isinstance(ip, str)
    
    def test_get_nodes(self, manager):
        """Test getting nodes."""
        nodes = manager.get_nodes()
        assert isinstance(nodes, dict)
        assert "test_node_1" in nodes
    
    def test_get_node_count(self, manager):
        """Test getting node count."""
        count = manager.get_node_count()
        assert count == 1
    
    def test_is_leader(self, manager):
        """Test leader election."""
        # With only one node, it should be the leader
        assert manager.is_leader() is True
    
    def test_get_leader(self, manager):
        """Test getting leader."""
        leader = manager.get_leader()
        assert leader == "test_node_1"
    
    def test_add_sync_item(self, manager):
        """Test adding sync item."""
        sync_item = {
            'type': 'test',
            'data': 'test data'
        }
        manager.add_sync_item(sync_item)
        # Queue should have one item
        assert not manager.sync_queue.empty()


class TestDataSynchronizer:
    """Test data synchronization utility."""
    
    def test_sync_data(self):
        """Test data synchronization."""
        source = {
            'a': 1,
            'b': {
                'c': 2,
                'd': 3
            },
            'e': [1, 2, 3]
        }
        
        target = {
            'a': 0,
            'b': {
                'c': 2,
                'f': 4
            },
            'g': 5
        }
        
        result = DataSynchronizer.sync_data(source, target)
        assert result['a'] == 1  # Override from source
        assert result['b']['c'] == 2  # Same value
        assert result['b']['d'] == 3  # Added from source
        assert result['b']['f'] == 4  # Kept from target
        assert result['e'] == [1, 2, 3]  # Added from source
        assert result['g'] == 5  # Kept from target
    
    def test_calculate_hash(self):
        """Test hash calculation."""
        data = {'a': 1, 'b': 2}
        hash1 = DataSynchronizer.calculate_hash(data)
        hash2 = DataSynchronizer.calculate_hash(data)
        assert hash1 == hash2  # Same data should have same hash
        
        # Different data should have different hash
        data2 = {'a': 1, 'b': 3}
        hash3 = DataSynchronizer.calculate_hash(data2)
        assert hash1 != hash3
    
    def test_detect_changes(self):
        """Test detecting changes."""
        old_data = {
            'a': 1,
            'b': {
                'c': 2,
                'd': 3
            },
            'e': [1, 2, 3]
        }
        
        new_data = {
            'a': 1,
            'b': {
                'c': 5,
                'f': 4
            },
            'g': 6
        }
        
        changes = DataSynchronizer.detect_changes(old_data, new_data)
        assert len(changes) == 5  # 1 modify, 2 add, 2 remove
        
        # Check changes
        change_types = [c['type'] for c in changes]
        assert 'modify' in change_types
        assert change_types.count('add') == 2
        assert change_types.count('remove') == 2
