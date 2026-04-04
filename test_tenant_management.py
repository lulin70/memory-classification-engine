"""Test tenant management functionality."""

import pytest
from memory_classification_engine import MemoryClassificationEngine


def test_tenant_creation():
    """Test tenant creation."""
    engine = MemoryClassificationEngine()
    
    # Test personal tenant creation
    personal_tenant = engine.create_tenant(
        'user123',
        'John Doe',
        'personal',
        user_id='user123'
    )
    assert personal_tenant['success'] == True
    assert personal_tenant['tenant_id'] == 'user123'
    assert personal_tenant['type'] == 'personal'
    
    # Test enterprise tenant creation
    enterprise_tenant = engine.create_tenant(
        'company123',
        'Acme Corporation',
        'enterprise',
        organization_id='org123'
    )
    assert enterprise_tenant['success'] == True
    assert enterprise_tenant['tenant_id'] == 'company123'
    assert enterprise_tenant['type'] == 'enterprise'


def test_tenant_retrieval():
    """Test tenant retrieval."""
    engine = MemoryClassificationEngine()
    
    # Create a tenant
    engine.create_tenant('user456', 'Jane Smith', 'personal', user_id='user456')
    
    # Get tenant
    tenant = engine.get_tenant('user456')
    assert tenant['success'] == True
    assert tenant['tenant_id'] == 'user456'
    assert tenant['name'] == 'Jane Smith'
    
    # Get non-existent tenant
    non_existent = engine.get_tenant('non-existent')
    assert non_existent['success'] == False


def test_tenant_listing():
    """Test tenant listing."""
    engine = MemoryClassificationEngine()
    
    # Create tenants
    engine.create_tenant('user789', 'Alice Johnson', 'personal', user_id='user789')
    engine.create_tenant('company789', 'Tech Inc', 'enterprise', organization_id='org789')
    
    # List tenants
    tenants = engine.list_tenants()
    assert len(tenants) >= 2
    tenant_ids = [t['tenant_id'] for t in tenants]
    assert 'user789' in tenant_ids
    assert 'company789' in tenant_ids


def test_tenant_update():
    """Test tenant update."""
    engine = MemoryClassificationEngine()
    
    # Create tenant
    engine.create_tenant('user321', 'Bob Brown', 'personal', user_id='user321')
    
    # Update tenant
    update_result = engine.update_tenant('user321', {'name': 'Robert Brown'})
    assert update_result['success'] == True
    assert update_result['name'] == 'Robert Brown'
    
    # Verify update
    updated_tenant = engine.get_tenant('user321')
    assert updated_tenant['name'] == 'Robert Brown'


def test_tenant_deletion():
    """Test tenant deletion."""
    engine = MemoryClassificationEngine()
    
    # Create tenant
    engine.create_tenant('user654', 'Charlie Davis', 'personal', user_id='user654')
    
    # Delete tenant
    delete_result = engine.delete_tenant('user654')
    assert delete_result['success'] == True
    
    # Verify deletion
    deleted_tenant = engine.get_tenant('user654')
    assert deleted_tenant['success'] == False


def test_enterprise_roles():
    """Test enterprise tenant roles and permissions."""
    engine = MemoryClassificationEngine()
    
    # Create enterprise tenant
    engine.create_tenant('company321', 'Global Corp', 'enterprise', organization_id='org321')
    
    # Add role
    add_role_result = engine.add_tenant_role(
        'company321',
        'admin',
        ['read', 'write', 'delete', 'manage_users']
    )
    assert add_role_result['success'] == True
    
    # Check permission
    check_permission = engine.check_tenant_permission('company321', 'admin', 'read')
    assert check_permission['success'] == True
    assert check_permission['has_permission'] == True
    
    # Check non-existent permission
    check_no_permission = engine.check_tenant_permission('company321', 'admin', 'unknown')
    assert check_no_permission['success'] == True
    assert check_no_permission['has_permission'] == False


def test_tenant_memory_management():
    """Test tenant memory management."""
    engine = MemoryClassificationEngine()
    
    # Create tenant
    engine.create_tenant('user987', 'David Wilson', 'personal', user_id='user987')
    
    # Process message with tenant context
    context = {'tenant_id': 'user987'}
    result = engine.process_message('I like coffee', context)
    assert result['tenant_id'] == 'user987'
    assert len(result['matches']) > 0
    
    # Retrieve memories for tenant
    tenant_memories = engine.get_tenant_memories('user987')
    assert len(tenant_memories) > 0
    
    # Retrieve memories with tenant filter
    filtered_memories = engine.retrieve_memories('coffee', tenant_id='user987')
    assert len(filtered_memories) > 0
    
    # Retrieve memories without tenant filter should include the memory
    all_memories = engine.retrieve_memories('coffee')
    assert len(all_memories) > 0


if __name__ == '__main__':
    # Run all tests
    test_tenant_creation()
    print("✓ test_tenant_creation passed")
    
    test_tenant_retrieval()
    print("✓ test_tenant_retrieval passed")
    
    test_tenant_listing()
    print("✓ test_tenant_listing passed")
    
    test_tenant_update()
    print("✓ test_tenant_update passed")
    
    test_tenant_deletion()
    print("✓ test_tenant_deletion passed")
    
    test_enterprise_roles()
    print("✓ test_enterprise_roles passed")
    
    test_tenant_memory_management()
    print("✓ test_tenant_memory_management passed")
    
    print("\nAll tests passed!")
