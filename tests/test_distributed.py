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
    
    def test_update_node_metrics(self, manager):
        """Test updating node metrics."""
        metrics = {
            'cpu_usage': 50.0,
            'memory_usage': 60.0,
            'disk_usage': 70.0
        }
        manager.update_node_metrics(metrics)
        node_metrics = manager.get_node_metrics(manager.node_id)
        assert node_metrics['cpu_usage'] == 50.0
        assert node_metrics['memory_usage'] == 60.0
    
    def test_add_task(self, manager):
        """Test adding a task."""
        task = {
            'id': 'task1',
            'type': 'test',
            'data': 'test data'
        }
        manager.add_task(task)
        assert not manager.task_queue.empty()
    
    def test_assign_tasks(self, manager):
        """Test task assignment."""
        # Add a task
        task = {
            'id': 'task1',
            'type': 'test',
            'data': 'test data'
        }
        manager.add_task(task)
        
        # Assign tasks
        manager.assign_tasks()
        
        # Check if task was assigned
        assignments = manager.get_task_assignments()
        assert manager.node_id in assignments
        assert len(assignments[manager.node_id]) > 0
    
    def test_get_node_health(self, manager):
        """Test node health check."""
        # Test healthy status
        metrics = {
            'cpu_usage': 30.0,
            'memory_usage': 40.0
        }
        manager.update_node_metrics(metrics)
        health = manager.get_node_health(manager.node_id)
        assert health == 'healthy'
        
        # Test warning status
        metrics = {
            'cpu_usage': 70.0,
            'memory_usage': 50.0
        }
        manager.update_node_metrics(metrics)
        health = manager.get_node_health(manager.node_id)
        assert health == 'warning'
        
        # Test critical status
        metrics = {
            'cpu_usage': 90.0,
            'memory_usage': 85.0
        }
        manager.update_node_metrics(metrics)
        health = manager.get_node_health(manager.node_id)
        assert health == 'critical'
    
    def test_get_cluster_health(self, manager):
        """Test cluster health check."""
        health_status = manager.get_cluster_health()
        assert isinstance(health_status, dict)
        assert manager.node_id in health_status
    
    def test_get_cluster_status(self, manager):
        """Test getting cluster status."""
        status = manager.get_cluster_status()
        assert isinstance(status, dict)
        assert 'cluster_size' in status
        assert 'leader' in status
        assert 'nodes' in status
    
    def test_get_performance_metrics(self, manager):
        """Test getting performance metrics."""
        metrics = manager.get_performance_metrics()
        assert isinstance(metrics, dict)
        assert 'node_count' in metrics
        assert 'average_cpu_usage' in metrics
    
    def test_get_raft_status(self, manager):
        """Test getting Raft status."""
        raft_status = manager.get_raft_status()
        assert isinstance(raft_status, dict)
        assert 'current_term' in raft_status
        assert 'state' in raft_status
    
    def test_generate_cluster_report(self, manager):
        """Test generating cluster report."""
        report = manager.generate_cluster_report()
        assert isinstance(report, str)
        assert 'Cluster Report' in report
    
    def test_message_compression(self, manager):
        """Test message compression."""
        message = {
            'type': 'test',
            'data': 'test data'
        }
        compressed = manager._compress_message(message)
        assert isinstance(compressed, bytes)
        decompressed = manager._decompress_message(compressed)
        assert decompressed['type'] == 'test'
        assert decompressed['data'] == 'test data'


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
    
    def test_incremental_sync(self):
        """Test incremental synchronization."""
        source = {
            'a': 1,
            'b': {
                'c': 2,
                'd': 3
            }
        }
        
        target = {
            'a': 0,
            'b': {
                'c': 2,
                'f': 4
            }
        }
        
        result, changes = DataSynchronizer.incremental_sync(source, target)
        assert result['a'] == 1
        assert result['b']['d'] == 3
        assert len(changes) > 0
    
    def test_resolve_conflicts(self):
        """Test conflict resolution."""
        conflicts = [
            {
                'type': 'modify',
                'path': 'a',
                'old_value': 0,
                'new_value': 1
            },
            {
                'type': 'add',
                'path': 'b',
                'value': 2
            }
        ]
        
        resolved = DataSynchronizer.resolve_conflicts(conflicts, 'latest')
        assert resolved['a'] == 1
        assert resolved['b'] == 2
    
    def test_calculate_merkle_tree(self):
        """Test Merkle tree calculation."""
        data = {
            'a': 1,
            'b': {
                'c': 2,
                'd': 3
            }
        }
        
        merkle_tree = DataSynchronizer.calculate_merkle_tree(data)
        assert isinstance(merkle_tree, dict)
        assert '' in merkle_tree  # Root hash
    
    def test_find_differences(self):
        """Test finding differences between Merkle trees."""
        data1 = {'a': 1, 'b': 2}
        data2 = {'a': 1, 'b': 3}
        
        tree1 = DataSynchronizer.calculate_merkle_tree(data1)
        tree2 = DataSynchronizer.calculate_merkle_tree(data2)
        
        differences = DataSynchronizer.find_differences(tree1, tree2)
        assert len(differences) > 0
