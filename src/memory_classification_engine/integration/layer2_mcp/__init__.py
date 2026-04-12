"""
MCP Server for Memory Classification Engine

This module provides a Model Context Protocol (MCP) server implementation
that allows Claude Code, Cursor, and other MCP clients to interact with
the Memory Classification Engine.

Usage:
    python -m memory_classification_engine.integration.layer2_mcp

Configuration:
    Set MCE_CONFIG_PATH environment variable to point to your config file.
    Set MCE_DATA_PATH environment variable to point to your data directory.
"""

from .server import MCPServer
from .tools import TOOLS
from .handlers import Handlers

__version__ = "0.1.0"
__all__ = ["MCPServer", "TOOLS", "Handlers"]
