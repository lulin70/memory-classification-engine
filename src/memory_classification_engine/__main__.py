"""
Entry point for running Memory Classification Engine as a module.

Usage:
    python -m memory_classification_engine
    python -m memory_classification_engine.mcp  # Comment in Chinese removedr
"""

import sys
import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Memory Classification Engine",
        prog="python -m memory_classification_engine"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Comment in Chinese removednd
    mcp_parser = subparsers.add_parser(
        "mcp",
        help="Run MCP Server"
    )
    mcp_parser.add_argument(
        "--config",
        help="Path to configuration file"
    )
    mcp_parser.add_argument(
        "--data-path",
        help="Path to data directory"
    )
    
    # Comment in Chinese removednd
    version_parser = subparsers.add_parser(
        "version",
        help="Show version information"
    )
    
    args = parser.parse_args()
    
    if args.command == "mcp":
        # Comment in Chinese removedr
        import asyncio
        import os
        from memory_classification_engine.integration.layer2_mcp.server import MCPServer
        
        if args.config:
            os.environ["MCE_CONFIG_PATH"] = args.config
        if args.data_path:
            os.environ["MCE_DATA_PATH"] = args.data_path
        
        server = MCPServer()
        asyncio.run(server.start())
    
    elif args.command == "version":
        from memory_classification_engine import __version__
        print(f"Memory Classification Engine v{__version__}")
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
