"""
Unit tests for MCP Server implementation.

This module tests the MCP Server, tools, and handlers
to ensure they work correctly according to the MCP specification.
"""

import json
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from memory_classification_engine.integration.layer2_mcp.server import MCPServer
from memory_classification_engine.integration.layer2_mcp.tools import (
    TOOLS, TOOL_NAMES, get_tool_schema, validate_tool_arguments
)
from memory_classification_engine.integration.layer2_mcp.handlers import Handlers


class TestMCPTools:
    """Tests for MCP tools definitions."""
    
    def test_all_tools_defined(self):
        """Test that all 11 tools are defined."""
        expected_tools = {
            "classify_memory",
            "store_memory",
            "retrieve_memories",
            "get_memory_stats",
            "batch_classify",
            "find_similar",
            "export_memories",
            "import_memories",
            "mce_recall",
            "mce_status",
            "mce_forget"
        }
        assert TOOL_NAMES == expected_tools
    
    def test_tool_schemas_valid(self):
        """Test that all tool schemas are valid."""
        for tool in TOOLS:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"
    
    def test_get_tool_schema(self):
        """Test getting tool schema."""
        schema = get_tool_schema("classify_memory")
        assert schema["name"] == "classify_memory"
        assert "message" in schema["inputSchema"]["properties"]
    
    def test_get_tool_schema_not_found(self):
        """Test getting non-existent tool schema."""
        with pytest.raises(ValueError):
            get_tool_schema("non_existent_tool")
    
    def test_validate_tool_arguments_valid(self):
        """Test validating valid tool arguments."""
        arguments = {"message": "Test message"}
        errors = validate_tool_arguments("classify_memory", arguments)
        assert len(errors) == 0
    
    def test_validate_tool_arguments_missing_required(self):
        """Test validating arguments with missing required field."""
        arguments = {}
        errors = validate_tool_arguments("classify_memory", arguments)
        assert len(errors) > 0
        assert any("Missing required field" in e for e in errors)
    
    def test_validate_tool_arguments_invalid_type(self):
        """Test validating arguments with invalid type."""
        arguments = {"message": 123}  # Should be string
        errors = validate_tool_arguments("classify_memory", arguments)
        assert len(errors) > 0
        assert any("must be a string" in e for e in errors)
    
    def test_validate_tool_arguments_invalid_enum(self):
        """Test validating arguments with invalid enum value."""
        arguments = {
            "content": "Test content",
            "memory_type": "invalid_type"  # Should be valid enum
        }
        errors = validate_tool_arguments("store_memory", arguments)
        assert len(errors) > 0
        assert any("must be one of" in e for e in errors)


class TestMCPHandlers:
    """Tests for MCP handlers."""
    
    @pytest.fixture
    def mock_engine(self):
        """Create a mock engine facade."""
        with patch('memory_classification_engine.integration.layer2_mcp.handlers.MemoryClassificationEngineFacade') as mock:
            engine = Mock()
            engine.process_message = Mock(return_value={
                "matched": True,
                "memory_type": "user_preference",
                "tier": 2,
                "content": "Test content",
                "confidence": 0.95,
                "source": "rule_matcher",
                "reasoning": "Matched preference pattern"
            })
            engine.storage_service = Mock()
            engine.storage_service.store_memory = Mock(return_value="memory_123")
            engine.storage_service.retrieve_memories = Mock(return_value=[
                {"id": "mem1", "type": "user_preference", "content": "Test memory"}
            ])
            engine.storage_service.get_stats = Mock(return_value={
                "total_memories": 10,
                "by_tier": {"2": 5, "3": 3, "4": 2}
            })
            mock.return_value = engine
            yield engine
    
    @pytest.fixture
    def handlers(self, mock_engine):
        """Create handlers with mock engine."""
        return Handlers()
    
    @pytest.mark.asyncio
    async def test_handle_classify_memory(self, handlers):
        """Test classify_memory handler."""
        arguments = {"message": "I prefer dark mode"}
        result = await handlers.handle_classify_memory(arguments)
        
        assert result["success"] is True
        assert result["matched"] is True
        assert result["memory_type"] == "user_preference"
        assert result["confidence"] == 0.95
    
    @pytest.mark.asyncio
    async def test_handle_store_memory(self, handlers):
        """Test store_memory handler."""
        arguments = {
            "content": "Test memory content",
            "memory_type": "user_preference",
            "tier": 2
        }
        result = await handlers.handle_store_memory(arguments)
        
        assert result["success"] is True
        assert result["stored"] is True
        assert result["memory_id"] == "memory_123"
    
    @pytest.mark.asyncio
    async def test_handle_retrieve_memories(self, handlers):
        """Test retrieve_memories handler."""
        arguments = {"query": "preference", "limit": 5}
        result = await handlers.handle_retrieve_memories(arguments)
        
        assert result["success"] is True
        assert result["count"] == 1
        assert len(result["memories"]) == 1
    
    @pytest.mark.asyncio
    async def test_handle_get_memory_stats(self, handlers):
        """Test get_memory_stats handler."""
        arguments = {}
        result = await handlers.handle_get_memory_stats(arguments)
        
        assert result["success"] is True
        assert result["stats"]["total_memories"] == 10
    
    @pytest.mark.asyncio
    async def test_handle_batch_classify(self, handlers):
        """Test batch_classify handler."""
        arguments = {
            "messages": [
                {"message": "Message 1"},
                {"message": "Message 2"}
            ]
        }
        result = await handlers.handle_batch_classify(arguments)
        
        assert result["success"] is True
        assert result["total"] == 2
        assert len(result["results"]) == 2
    
    @pytest.mark.asyncio
    async def test_handle_tool_unknown(self, handlers):
        """Test handling unknown tool."""
        with pytest.raises(ValueError) as exc_info:
            await handlers.handle_tool("unknown_tool", {})
        assert "Unknown tool" in str(exc_info.value)


class TestMCPServer:
    """Tests for MCP Server."""
    
    @pytest.fixture
    def server(self):
        """Create MCP server instance."""
        with patch('memory_classification_engine.integration.layer2_mcp.server.Handlers'):
            server = MCPServer()
            yield server
    
    @pytest.mark.asyncio
    async def test_handle_initialize(self, server):
        """Test initialize request handling."""
        request_id = 1
        params = {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
        
        response = await server.handle_initialize(request_id, params)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == request_id
        assert response["result"]["protocolVersion"] == "2024-11-05"
        assert response["result"]["serverInfo"]["name"] == "memory-classification-engine-mcp"
    
    @pytest.mark.asyncio
    async def test_handle_tools_list(self, server):
        """Test tools/list request handling."""
        request_id = 1
        
        response = await server.handle_tools_list(request_id)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == request_id
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) == 11
    
    @pytest.mark.asyncio
    async def test_handle_tools_call(self, server):
        """Test tools/call request handling."""
        request_id = 1
        params = {
            "name": "classify_memory",
            "arguments": {"message": "Test message"}
        }
        
        # Mock the handlers
        server.handlers.handle_tool = AsyncMock(return_value={
            "success": True,
            "matched": True
        })
        
        response = await server.handle_tools_call(request_id, params)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == request_id
        assert "result" in response
        assert "content" in response["result"]
    
    @pytest.mark.asyncio
    async def test_handle_shutdown(self, server):
        """Test shutdown request handling."""
        request_id = 1
        
        response = await server.handle_shutdown(request_id)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == request_id
        assert response["result"] is None
    
    @pytest.mark.asyncio
    async def test_handle_request_unknown_method(self, server):
        """Test handling unknown method."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "unknown_method",
            "params": {}
        }
        
        response = await server.handle_request(request)
        
        assert response is not None
        assert "error" in response
        assert response["error"]["code"] == -32601
        assert "Method not found" in response["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_send_error(self, server):
        """Test sending error response."""
        request_id = 1
        code = -32600
        message = "Invalid Request"
        
        response = await server.send_error(request_id, code, message)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == request_id
        assert response["error"]["code"] == code
        assert response["error"]["message"] == message


class TestMCPIntegration:
    """Integration tests for MCP Server."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test a full workflow: initialize -> tools/list -> tool call."""
        with patch('memory_classification_engine.integration.layer2_mcp.server.Handlers') as mock_handlers:
            # Setup mock
            mock_handlers_instance = Mock()
            mock_handlers_instance.handle_tool = AsyncMock(return_value={
                "success": True,
                "matched": True,
                "memory_type": "user_preference"
            })
            mock_handlers.return_value = mock_handlers_instance

            server = MCPServer()

            # Step 1: Initialize
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {"name": "test", "version": "1.0"}
                }
            }
            response = await server.handle_request(init_request)
            assert response["result"]["protocolVersion"] == "2024-11-05"

            # Step 2: List tools
            list_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            response = await server.handle_request(list_request)
            assert len(response["result"]["tools"]) == 11
            
            # Step 3: Call tool
            call_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "classify_memory",
                    "arguments": {
                        "message": "I prefer using double quotes"
                    }
                }
            }
            response = await server.handle_request(call_request)
            assert response["result"]["content"][0]["type"] == "text"

            # Step 4: Shutdown
            shutdown_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "shutdown"
            }
            response = await server.handle_request(shutdown_request)
            assert response["result"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
