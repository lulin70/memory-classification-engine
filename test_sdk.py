"""Test SDK functionality."""

from memory_classification_engine.sdk.python import MemorySDK, MemoryClient


def test_memory_sdk_local():
    """Test MemorySDK in local mode."""
    print("Testing MemorySDK in local mode...")
    
    sdk = MemorySDK()
    
    # Test process message
    process_result = sdk.process_message("I like coffee")
    print(f"Process message result: {process_result}")
    
    # Test retrieve memories
    retrieve_result = sdk.retrieve_memories("coffee")
    print(f"Retrieve memories result: {retrieve_result}")
    
    # Test create tenant
    create_tenant_result = sdk.create_tenant(
        'test-sdk-tenant',
        'Test SDK Tenant',
        'personal',
        user_id='test-sdk-user'
    )
    print(f"Create tenant result: {create_tenant_result}")
    
    # Test list tenants
    list_tenants_result = sdk.list_tenants()
    print(f"List tenants result: {list_tenants_result}")
    
    # Test get tenant
    get_tenant_result = sdk.get_tenant('test-sdk-tenant')
    print(f"Get tenant result: {get_tenant_result}")
    
    # Test process message with tenant context
    process_with_tenant = sdk.process_message(
        "I like tea",
        context={'tenant_id': 'test-sdk-tenant'}
    )
    print(f"Process message with tenant result: {process_with_tenant}")
    
    # Test retrieve memories with tenant
    retrieve_with_tenant = sdk.retrieve_memories(
        "tea",
        tenant_id='test-sdk-tenant'
    )
    print(f"Retrieve memories with tenant result: {retrieve_with_tenant}")
    
    # Test get tenant memories
    tenant_memories = sdk.get_tenant_memories('test-sdk-tenant')
    print(f"Get tenant memories result: {tenant_memories}")
    
    # Test delete tenant
    delete_tenant_result = sdk.delete_tenant('test-sdk-tenant')
    print(f"Delete tenant result: {delete_tenant_result}")
    
    # Test get stats
    stats = sdk.get_stats()
    print(f"Get stats result: {stats}")
    
    print("Local SDK tests completed!")


def test_memory_client():
    """Test MemoryClient."""
    print("\nTesting MemoryClient...")
    
    client = MemoryClient()
    
    # Test remember
    remember_result = client.remember("I like chocolate")
    print(f"Remember result: {remember_result}")
    
    # Test recall
    recall_result = client.recall("chocolate")
    print(f"Recall result: {recall_result}")
    
    # Test stats
    stats = client.stats()
    print(f"Stats result: {stats}")
    
    # Test clear
    client.clear()
    print("Working memory cleared")
    
    print("MemoryClient tests completed!")


def test_sdk_api_mode():
    """Test MemorySDK in API mode (if API server is running)."""
    print("\nTesting MemorySDK in API mode...")
    
    try:
        sdk = MemorySDK(api_url='http://localhost:8000')
        
        # Test health check via process message
        process_result = sdk.process_message("API mode test")
        print(f"API mode process message result: {process_result}")
        
        # Test retrieve memories
        retrieve_result = sdk.retrieve_memories("test")
        print(f"API mode retrieve memories result: {retrieve_result}")
        
        print("API mode tests completed!")
    except Exception as e:
        print(f"API mode test failed (server might not be running): {e}")


if __name__ == '__main__':
    # Run local SDK test
    test_memory_sdk_local()
    
    # Run MemoryClient test
    test_memory_client()
    
    # Run API mode test
    test_sdk_api_mode()
    
    print("\nAll SDK tests completed!")
