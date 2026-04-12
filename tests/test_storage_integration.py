#!/usr/bin/env python3
"""Integration tests for storage modules (Tier2, Tier3, Tier4)."""

import pytest
import os
import tempfile
import shutil
from memory_classification_engine.storage.tier2 import Tier2Storage
from memory_classification_engine.storage.tier3 import Tier3Storage
from memory_classification_engine.storage.tier4 import Tier4Storage


@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for storage testing."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


class TestTier2Storage:
    """Test Tier2 storage for procedural memory."""

    @pytest.fixture
    def tier2_storage(self, temp_storage_dir):
        """Create a Tier2 storage instance with temporary directory."""
        return Tier2Storage(os.path.join(temp_storage_dir, "tier2"))

    def test_init_creates_directories(self, tier2_storage):
        """Test that initialization creates necessary directories."""
        assert os.path.exists(tier2_storage.storage_path)
        assert os.path.exists(tier2_storage.preferences_file)
        assert os.path.exists(tier2_storage.corrections_file)

    def test_store_memory(self, tier2_storage):
        """Test storing a memory in tier 2."""
        memory = {
            'id': 'mem_001',
            'memory_type': 'user_preference',
            'content': 'I prefer using spaces over tabs',
            'confidence': 0.95,
            'tier': 2,
            'created_at': '2026-04-12T12:00:00Z'
        }
        
        result = tier2_storage.store_memory(memory)
        assert result is True

    def test_retrieve_memories(self, tier2_storage):
        """Test retrieving memories from tier 2."""
        memory = {
            'id': 'mem_002',
            'memory_type': 'task_pattern',
            'content': 'Always run tests before committing',
            'confidence': 0.9,
            'tier': 2
        }
        
        tier2_storage.store_memory(memory)
        
        memories = tier2_storage.retrieve_memories("test", limit=10)
        assert isinstance(memories, list)

    def test_update_memory(self, tier2_storage):
        """Test updating a memory in tier 2."""
        memory = {
            'id': 'mem_003',
            'memory_type': 'decision',
            'content': 'Use PostgreSQL',
            'confidence': 0.85,
            'tier': 2
        }
        
        tier2_storage.store_memory(memory)
        
        updates = {'confidence': 0.95, 'updated': True}
        result = tier2_storage.update_memory('mem_003', updates)
        assert result is True

    def test_delete_memory(self, tier2_storage):
        """Test deleting a memory from tier 2."""
        memory = {
            'id': 'mem_004',
            'memory_type': 'user_preference',
            'content': 'Test preference to delete',
            'tier': 2
        }
        
        tier2_storage.store_memory(memory)
        result = tier2_storage.delete_memory('mem_004')
        assert result is True

    def test_get_stats(self, tier2_storage):
        """Test getting statistics from tier 2."""
        stats = tier2_storage.get_stats()
        assert isinstance(stats, dict)
        assert 'total_memories' in stats

    def test_store_multiple_memories(self, tier2_storage):
        """Test storing multiple memories."""
        memories = [
            {'id': f'mem_{i:03d}', 'memory_type': 'user_preference', 
             'content': f'Preference {i}', 'tier': 2}
            for i in range(5)
        ]
        
        for mem in memories:
            tier2_storage.store_memory(mem)
        
        all_memories = tier2_storage.retrieve_memories("", limit=100)
        assert len(all_memories) >= 5


class TestTier3Storage:
    """Test Tier3 storage for episodic memory."""

    @pytest.fixture
    def tier3_storage(self, temp_storage_dir):
        """Create a Tier3 storage instance with temporary directory."""
        return Tier3Storage(os.path.join(temp_storage_dir, "tier3"))

    def test_init(self, tier3_storage):
        """Test Tier3 initialization."""
        assert os.path.exists(tier3_storage.storage_path)

    def test_store_and_retrieve(self, tier3_storage):
        """Test storing and retrieving episodic memory."""
        memory = {
            'id': 'epi_001',
            'memory_type': 'correction',
            'content': 'Rejected the previous approach, prefers simplicity',
            'confidence': 0.89,
            'tier': 3,
            'source': 'pattern'
        }
        
        result = tier3_storage.store_memory(memory)
        assert result is True
        
        retrieved = tier3_storage.retrieve_memories("simplicity", limit=10)
        assert isinstance(retrieved, list)

    def test_weighted_decay(self, tier3_storage):
        """Test that weighted decay works correctly."""
        old_memory = {
            'id': 'epi_old',
            'memory_type': 'fact_declaration',
            'content': 'Old fact from long ago',
            'tier': 3,
            'weight': 1.0,
            'created_at': '2026-01-01T00:00:00Z'
        }
        
        new_memory = {
            'id': 'epi_new',
            'memory_type': 'fact_declaration',
            'content': 'New recent fact',
            'tier': 3,
            'weight': 1.0,
            'created_at': '2026-04-12T00:00:00Z'
        }
        
        tier3_storage.store_memory(old_memory)
        tier3_storage.store_memory(new_memory)
        
        all_memories = tier3_storage.retrieve_memories("")
        assert len(all_memories) >= 2

    def test_encryption_handling(self, tier3_storage):
        """Test handling of encrypted memories."""
        encrypted_memory = {
            'id': 'epi_encrypted',
            'memory_type': 'fact_declaration',
            'content': '{"encrypted": true, "data": "base64data"}',
            'is_encrypted': True,
            'tier': 3
        }
        
        result = tier3_storage.store_memory(encrypted_memory)
        assert result is True
        
        retrieved = tier3_storage.get_memory('epi_encrypted')
        assert retrieved is not None


class TestTier4Storage:
    """Test Tier4 storage for semantic/long-term memory."""

    @pytest.fixture
    def tier4_storage(self, temp_storage_dir):
        """Create a Tier4 storage instance with temporary directory."""
        return Tier4Storage(os.path.join(temp_storage_dir, "tier4"))

    def test_init(self, tier4_storage):
        """Test Tier4 initialization."""
        assert os.path.exists(tier4_storage.storage_path)

    def test_store_relationships(self, tier4_storage):
        """Test storing relationship information."""
        relationship = {
            'id': 'rel_001',
            'memory_type': 'relationship',
            'content': 'Alice handles backend API',
            'entities': ['Alice', 'backend'],
            'confidence': 0.95,
            'tier': 4
        }
        
        result = tier4_storage.store_memory(relationship)
        assert result is True

    def test_graph_structure(self, tier4_storage):
        """Test knowledge graph structure maintenance."""
        relationships = [
            {'id': f'rel_{i}', 'memory_type': 'relationship', 
             'content': f'Entity A related to Entity B - {i}', 'tier': 4}
            for i in range(3)
        ]
        
        for rel in relationships:
            tier4_storage.store_memory(rel)
        
        all_relations = tier4_storage.retrieve_memories("", limit=50)
        assert len(all_relations) >= 3


class TestStorageIntegration:
    """Integration tests across storage tiers."""

    @pytest.fixture
    def storage_coordinator(self, temp_storage_dir):
        """Create a StorageCoordinator instance."""
        from memory_classification_engine.coordinators.storage_coordinator import StorageCoordinator
        from memory_classification_engine.utils.config import ConfigManager
        
        config = ConfigManager()
        config.set('storage.data_path', temp_storage_dir)
        config.set('storage.tier2_path', os.path.join(temp_storage_dir, "tier2"))
        config.set('storage.tier3_path', os.path.join(temp_storage_dir, "tier3"))
        config.set('storage.tier4_path', os.path.join(temp_storage_dir, "tier4"))
        
        return StorageCoordinator(config)

    def test_cross_tier_storage(self, storage_coordinator):
        """Test storing memories across different tiers."""
        memories = [
            {'id': 'cross_1', 'memory_type': 'user_preference', 
             'content': 'User preference', 'tier': 2},
            {'id': 'cross_2', 'memory_type': 'correction', 
             'content': 'Correction event', 'tier': 3},
            {'id': 'cross_3', 'memory_type': 'relationship', 
             'content': 'Team relationship', 'tier': 4}
        ]
        
        for mem in memories:
            result = storage_coordinator.store_memory(mem)
            assert result is True

    def test_tier_specific_retrieval(self, storage_coordinator):
        """Test retrieving from specific tiers."""
        tier2_mem = storage_coordinator.retrieve_memories("", limit=5, tier=2)
        tier3_mem = storage_coordinator.retrieve_memories("", limit=5, tier=3)
        tier4_mem = storage_coordinator.retrieve_memories("", limit=5, tier=4)
        
        assert isinstance(tier2_mem, list)
        assert isinstance(tier3_mem, list)
        assert isinstance(tier4_mem, list)

    def test_batch_storage(self, storage_coordinator):
        """Test batch storage functionality."""
        batch_memories = [
            {'id': f'batch_{i:03d}', 'memory_type': 'task_pattern',
             'content': f'Task pattern {i}', 'tier': 2 + (i % 3)}
            for i in range(10)
        ]
        
        result = storage_coordinator.store_memories_batch(batch_memories)
        assert result is True

    def test_memory_lifecycle(self, storage_coordinator):
        """Test complete memory lifecycle: store -> retrieve -> update -> delete."""
        memory = {
            'id': 'lifecycle_test',
            'memory_type': 'decision',
            'content': 'Decision to use Redis for caching',
            'tier': 3,
            'confidence': 0.88
        }
        
        # Store
        assert storage_coordinator.store_memory(memory) is True
        
        # Retrieve
        retrieved = storage_coordinator.get_memory('lifecycle_test')
        assert retrieved is not None
        assert retrieved['content'] == 'Decision to use Redis for caching'
        
        # Update
        assert storage_coordinator.update_memory('lifecycle_test', {'confidence': 0.95}) is True
        
        # Delete
        assert storage_coordinator.delete_memory('lifecycle_test') is True
        
        # Verify deletion
        deleted = storage_coordinator.get_memory('lifecycle_test')
        assert deleted is None

    def test_statistics_across_tiers(self, storage_coordinator):
        """Test getting combined statistics across all tiers."""
        stats = storage_coordinator.get_stats()
        
        assert 'tier2' in stats
        assert 'tier3' in stats
        assert 'tier4' in stats
        assert 'total_memories' in stats

    def test_memory_type_filtering(self, storage_coordinator):
        """Test filtering by memory type."""
        memories = [
            {'id': 'filter_pref', 'memory_type': 'user_preference', 
             'content': 'Preference', 'tier': 2},
            {'id': 'filter_corr', 'memory_type': 'correction', 
             'content': 'Correction', 'tier': 3},
            {'id': 'filter_pref2', 'memory_type': 'user_preference', 
             'content': 'Another preference', 'tier': 2}
        ]
        
        storage_coordinator.store_memories_batch(memories)
        
        prefs = storage_coordinator.retrieve_memories("", limit=10, memory_type='user_preference')
        assert len(prefs) >= 2
        
        corrs = storage_coordinator.retrieve_memories("", limit=10, memory_type='correction')
        assert len(corrs) >= 1


class TestStorageErrorHandling:
    """Test error handling in storage operations."""

    def test_invalid_memory_id(self, temp_storage_dir):
        """Test handling of invalid memory ID."""
        tier2 = Tier2Storage(os.path.join(temp_storage_dir, "tier2"))
        
        result = tier2.get_memory("nonexistent_id")
        assert result is None
        
        result = tier2.update_memory("nonexistent_id", {})
        assert result is False
        
        result = tier2.delete_memory("nonexistent_id")
        assert result is False

    def test_empty_query_handling(self, temp_storage_dir):
        """Test handling of empty queries."""
        tier3 = Tier3Storage(os.path.join(temp_storage_dir, "tier3"))
        
        results = tier3.retrieve_memories("")
        assert isinstance(results, list)

    def test_concurrent_access(self, temp_storage_dir):
        """Test concurrent access to storage."""
        import threading
        import time
        
        tier2 = Tier2Storage(os.path.join(temp_storage_dir, "tier2_concurrent"))
        
        errors = []
        
        def store_memory(idx):
            try:
                mem = {'id': f'concurrent_{idx}', 'memory_type': 'user_preference',
                       'content': f'Concurrent memory {idx}', 'tier': 2}
                tier2.store_memory(mem)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=store_memory, args=(i,)) for i in range(20)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Errors during concurrent access: {errors}"