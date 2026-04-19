"""
Unit tests for MCP Server implementation.

Pure Upstream Mode (v0.3.0): Only classification tools tested.
Storage/retrieval/CRUD handlers have been removed.
"""

import json
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from memory_classification_engine.integration.layer2_mcp.server import MCPServer
from memory_classification_engine.integration.layer2_mcp.tools import (
    TOOLS, TOOL_NAMES, get_tool_schema, validate_tool_arguments,
    CLASSIFICATION_SCHEMA
)
from memory_classification_engine.integration.layer2_mcp.handlers import (
    Handlers, handler_map, handle_classify_message,
    handle_get_classification_schema, handle_batch_classify, handle_mce_status
)


class TestMCPTools:
    """Tests for MCP tools definitions."""

    def test_all_tools_defined(self):
        """Test that all 4 core tools are defined (v0.3.0 Pure Upstream)."""
        expected_tools = {
            "classify_message",
            "get_classification_schema",
            "batch_classify",
            "mce_status"
        }
        assert TOOL_NAMES == expected_tools

    def test_tool_count(self):
        """Test exactly 4 tools in Pure Upstream mode."""
        assert len(TOOLS) == 4

    def test_tool_schemas_valid(self):
        """Test that all tool schemas are valid."""
        for tool in TOOLS:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"

    def test_get_tool_schema_classify_message(self):
        """Test getting classify_message schema."""
        schema = get_tool_schema("classify_message")
        assert schema["name"] == "classify_message"
        assert "message" in schema["inputSchema"]["properties"]

    def test_get_tool_schema_get_classification_schema(self):
        """Test getting get_classification_schema schema."""
        schema = get_tool_schema("get_classification_schema")
        assert schema["name"] == "get_classification_schema"
        assert "format" in schema["inputSchema"]["properties"]

    def test_get_tool_schema_not_found(self):
        """Test getting non-existent tool schema."""
        with pytest.raises(ValueError):
            get_tool_schema("non_existent_tool")

    def test_get_tool_schema_removed_tool_raises(self):
        """Test that removed storage tools raise ValueError."""
        for removed_tool in ["store_memory", "retrieve_memories", "mce_recall", "mce_forget"]:
            with pytest.raises(ValueError):
                get_tool_schema(removed_tool)

    def test_validate_tool_arguments_valid(self):
        """Test validating valid classify_message arguments."""
        arguments = {"message": "Test message"}
        errors = validate_tool_arguments("classify_message", arguments)
        assert len(errors) == 0

    def test_validate_tool_arguments_missing_required(self):
        """Test validating arguments with missing required field."""
        arguments = {}
        errors = validate_tool_arguments("classify_message", arguments)
        assert len(errors) > 0
        assert any("Missing required field" in e for e in errors)

    def test_validate_tool_arguments_invalid_type(self):
        """Test validating arguments with invalid type."""
        arguments = {"message": 123}
        errors = validate_tool_arguments("classify_message", arguments)
        assert len(errors) > 0
        assert any("must be a string" in e for e in errors)

    def test_validate_tool_arguments_invalid_enum_detail_level(self):
        """Test mce_status detail_level enum validation."""
        arguments = {"detail_level": "invalid"}
        errors = validate_tool_arguments("mce_status", arguments)
        assert len(errors) > 0
        assert any("must be one of" in e for e in errors)

    def test_classification_schema_exists(self):
        """Test CLASSIFICATION_SCHEMA constant is populated."""
        assert CLASSIFICATION_SCHEMA["schema_version"] == "1.0.0"
        assert len(CLASSIFICATION_SCHEMA["memory_types"]) == 7
        assert len(CLASSIFICATION_SCHEMA["storage_tiers"]) == 4


class TestMCPHandlers:
    """Tests for MCP handlers (Pure Upstream mode)."""

    @pytest.fixture
    def mock_engine(self):
        """Create a mock engine facade."""
        engine = Mock()
        engine.process_message = Mock(return_value={
            "matches": [{
                "memory_type": "user_preference",
                "tier": 2,
                "content": "User prefers dark mode",
                "confidence": 0.95,
                "source": "rule_matcher",
                "reasoning": "Matched preference pattern"
            }],
            "processing_time": 0.045
        })
        engine.ENGINE_VERSION = "0.3.0"
        return engine

    @pytest.fixture
    def handlers(self, mock_engine):
        """Create handlers with mock engine."""
        return Handlers()

    def test_handle_classify_message_returns_entry_format(self, mock_engine):
        """Test classify_message returns MemoryEntry Schema v1.0 format."""
        result = handle_classify_message(mock_engine, {"message": "I prefer dark mode"})

        assert result["schema_version"] == "1.0.0"
        assert result["should_remember"] is True
        assert len(result["entries"]) == 1
        entry = result["entries"][0]
        assert entry["type"] == "user_preference"
        assert entry["confidence"] == 0.95
        assert entry["tier"] == 2
        assert "suggested_action" in entry
        assert "id" in entry
        assert "metadata" in entry
        assert result["engine_info"]["mode"] == "classification_only"

    def test_handle_classify_message_empty_input(self, mock_engine):
        """Test classify_message with empty message."""
        result = handle_classify_message(mock_engine, {"message": ""})
        assert result["should_remember"] is False
        assert result["entries"] == []
        assert "error" in result

    def test_handle_classify_message_no_matches(self, mock_engine):
        """Test classify_message when nothing matches."""
        mock_engine.process_message = Mock(return_value={"matches": [], "processing_time": 0.01})
        result = handle_classify_message(mock_engine, {"message": "OK thanks"})
        assert result["should_remember"] is False
        assert result["entries"] == []

    def test_handle_get_classification_schema_json(self, mock_engine):
        """Test get_classification_schema returns JSON format."""
        result = handle_get_classification_schema(mock_engine, {"format": "json"})
        assert result["format"] == "json"
        schema = result["schema"]
        assert schema["schema_version"] == "1.0.0"
        assert len(schema["memory_types"]) == 7
        assert len(schema["storage_tiers"]) == 4
        assert "downstream_mapping" in schema["memory_types"][0]

    def test_handle_get_classification_schema_markdown(self, mock_engine):
        """Test get_classification_schema returns markdown format."""
        result = handle_get_classification_schema(mock_engine, {"format": "markdown"})
        assert result["format"] == "markdown"
        assert "# MCE Classification Schema" in result["schema"]
        assert "Memory Types" in result["schema"]

    def test_handle_batch_classify(self, mock_engine):
        """Test batch_classify returns per-message results."""
        result = handle_batch_classify(mock_engine, {
            "messages": [
                {"message": "I prefer dark mode"},
                {"message": "OK thanks"},
                {"message": "We chose Redis"}
            ]
        })
        assert "results" in result
        assert "summary" in result
        assert result["summary"]["total_messages"] == 3
        assert len(result["results"]) == 3
        assert isinstance(result["results"][0], dict)
        assert "schema_version" in result["results"][0]

    def test_handle_batch_classify_empty(self, mock_engine):
        """Test batch_classify with empty list."""
        result = handle_batch_classify(mock_engine, {"messages": []})
        assert result["summary"]["total_messages"] == 0
        assert "error" in result

    def test_handle_mce_status_summary(self, mock_engine):
        """Test mce_status returns summary info."""
        result = handle_mce_status(mock_engine, {"detail_level": "summary"})
        assert result["status"] == "active"
        assert result["mode"] == "classification_only"
        assert "version" in result
        assert "capabilities" in result
        assert result["capabilities"]["memory_types"] == 7
        assert "available_tools" in result["capabilities"]
        assert len(result["capabilities"]["available_tools"]) == 4
        assert "uptime_seconds" in result

    def test_handlers_backward_compat_handle_tool(self, mock_engine):
        """Test Handlers class async handle_tool routes correctly."""
        import asyncio
        h = Handlers()
        result = asyncio.get_event_loop().run_until_complete(
            h.handle_tool("classify_message", {"message": "test"})
        )
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["schema_version"] == "1.0.0"

    def test_handlers_handle_unknown_tool(self, mock_engine):
        """Test Handlers class handles unknown tool gracefully."""
        import asyncio
        h = Handlers()
        result = asyncio.get_event_loop().run_until_complete(
            h.handle_tool("store_memory_removed", {})
        )
        assert result["success"] is False
        assert "error" in result
        assert "Unknown tool" in result["error"]


class TestMCPServer:
    """Tests for MCP Server (Pure Upstream mode)."""

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
    async def test_handle_tools_list_4_tools(self, server):
        """Test tools/list returns exactly 4 tools."""
        request_id = 1
        response = await server.handle_tools_list(request_id)
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == request_id
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) == 4

    @pytest.mark.asyncio
    async def test_handle_tools_call_classify(self, server):
        """Test tools/call for classify_message."""
        request_id = 1
        params = {
            "name": "classify_message",
            "arguments": {"message": "Test message"}
        }
        server.handlers.handle_tool = AsyncMock(return_value={
            "success": True,
            "data": {"schema_version": "1.0.0", "should_remember": True, "entries": []}
        })
        response = await server.handle_tools_call(request_id, params)
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == request_id
        assert "result" in response

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


class TestMCPIntegration:
    """Integration tests for MCP Server (Pure Upstream mode)."""

    @pytest.mark.asyncio
    async def test_full_workflow_4_tools(self):
        """Test full workflow: initialize -> tools/list(4) -> tool call -> shutdown."""
        with patch('memory_classification_engine.integration.layer2_mcp.server.Handlers') as mock_handlers:
            mock_handlers_instance = Mock()
            mock_handlers_instance.handle_tool = AsyncMock(return_value={
                "success": True,
                "data": {
                    "schema_version": "1.0.0",
                    "should_remember": True,
                    "entries": [{"type": "user_preference"}],
                    "summary": {"total_entries": 1},
                    "engine_info": {"mode": "classification_only"}
                }
            })
            mock_handlers.return_value = mock_handlers_instance

            server = MCPServer()

            init_request = {
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "clientInfo": {"name": "test", "version": "1.0"}}
            }
            response = await server.handle_request(init_request)
            assert response["result"]["protocolVersion"] == "2024-11-05"

            list_request = {
                "jsonrpc": "2.0", "id": 2, "method": "tools/list"
            }
            response = await server.handle_request(list_request)
            assert len(response["result"]["tools"]) == 4

            call_request = {
                "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {
                    "name": "classify_message",
                    "arguments": {"message": "I prefer using double quotes"}
                }
            }
            response = await server.handle_request(call_request)
            assert response["result"]["content"][0]["type"] == "text"

            shutdown_request = {
                "jsonrpc": "2.0", "id": 4, "method": "shutdown"
            }
            response = await server.handle_request(shutdown_request)
            assert response["result"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
