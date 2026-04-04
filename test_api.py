"""Test API functionality."""

import asyncio
from memory_classification_engine.api.client import APIClient, SyncAPIClient


async def test_async_client():
    """Test async API client."""
    print("Testing async API client...")
    
    async with APIClient() as client:
        try:
            # Test health check
            health = await client.health_check()
            print(f"Health check: {health}")
            
            # Test process message
            process_result = await client.process_message("I like coffee")
            print(f"Process message result: {process_result}")
            
            # Test retrieve memories
            retrieve_result = await client.retrieve_memories("coffee")
            print(f"Retrieve memories result: {retrieve_result}")
            
            # Test create tenant
            create_tenant_result = await client.create_tenant(
                'test-tenant',
                'Test Tenant',
                'personal',
                user_id='test-user'
            )
            print(f"Create tenant result: {create_tenant_result}")
            
            # Test list tenants
            list_tenants_result = await client.list_tenants()
            print(f"List tenants result: {list_tenants_result}")
            
            # Test get tenant
            get_tenant_result = await client.get_tenant('test-tenant')
            print(f"Get tenant result: {get_tenant_result}")
            
            # Test process message with tenant context
            process_with_tenant = await client.process_message(
                "I like tea",
                context={'tenant_id': 'test-tenant'}
            )
            print(f"Process message with tenant result: {process_with_tenant}")
            
            # Test retrieve memories with tenant
            retrieve_with_tenant = await client.retrieve_memories(
                "tea",
                tenant_id='test-tenant'
            )
            print(f"Retrieve memories with tenant result: {retrieve_with_tenant}")
            
            # Test get tenant memories
            tenant_memories = await client.get_tenant_memories('test-tenant')
            print(f"Get tenant memories result: {tenant_memories}")
            
            # Test delete tenant
            delete_tenant_result = await client.delete_tenant('test-tenant')
            print(f"Delete tenant result: {delete_tenant_result}")
            
            # Test WebSocket functionality (if server is running)
            try:
                await client.connect_websocket()
                ws_result = await client.process_message_websocket("WebSocket test")
                print(f"WebSocket process message result: {ws_result}")
            except Exception as e:
                print(f"WebSocket test failed (server might not be running): {e}")
                
        except Exception as e:
            print(f"API client test failed: {e}")
            import traceback
            traceback.print_exc()


def test_sync_client():
    """Test sync API client."""
    print("\nTesting sync API client...")
    
    client = SyncAPIClient()
    
    try:
        # Test health check
        health = client.health_check()
        print(f"Health check: {health}")
        
        # Test process message
        process_result = client.process_message("I like coffee")
        print(f"Process message result: {process_result}")
        
        # Test retrieve memories
        retrieve_result = client.retrieve_memories("coffee")
        print(f"Retrieve memories result: {retrieve_result}")
        
    except Exception as e:
        print(f"Sync API client test failed: {e}")
        import traceback
        traceback.print_exc()


def test_api_server():
    """Test API server startup."""
    print("\nTesting API server startup...")
    
    import subprocess
    import time
    
    # Start the API server in a subprocess
    server_process = subprocess.Popen([
        'python3', '-m', 'memory_classification_engine.api.server',
        '--host', 'localhost',
        '--port', '8080'
    ])
    
    # Wait for the server to start
    time.sleep(2)
    
    try:
        # Test with sync client
        client = SyncAPIClient(base_url='http://localhost:8080')
        health = client.health_check()
        print(f"API server health check: {health}")
        
        # Test process message
        process_result = client.process_message("API server test")
        print(f"API server process message result: {process_result}")
        
    except Exception as e:
        print(f"API server test failed: {e}")
    finally:
        # Stop the server
        server_process.terminate()
        server_process.wait()
        print("API server stopped")


if __name__ == '__main__':
    # Run async client test
    asyncio.run(test_async_client())
    
    # Run sync client test
    test_sync_client()
    
    # Run API server test
    test_api_server()
    
    print("\nAPI tests completed!")
