#!/usr/bin/env python3
"""CarryMem CLI - Command Line Interface for CarryMem.

Usage:
    carrymem init       - Initialize CarryMem configuration
    carrymem list       - List all memories
    carrymem stats      - Show memory statistics
    carrymem doctor     - Run diagnostics
    carrymem version    - Show version information
    carrymem help       - Show this help message
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional
import argparse

try:
    from memory_classification_engine import CarryMem
    from memory_classification_engine.__version__ import __version__
except ImportError:
    print("❌ CarryMem not properly installed")
    print("💡 Try: pip install carrymem")
    sys.exit(1)


class CarryMemCLI:
    """Command Line Interface for CarryMem."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".carrymem"
        self.config_file = self.config_dir / "config.json"
        self.db_path = self.config_dir / "memories.db"
    
    def run(self, args: list):
        """Run CLI command."""
        parser = argparse.ArgumentParser(
            description="CarryMem - Your portable AI memory layer",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # init command
        subparsers.add_parser('init', help='Initialize CarryMem configuration')
        
        # list command
        list_parser = subparsers.add_parser('list', help='List all memories')
        list_parser.add_argument('--limit', type=int, default=10, help='Number of memories to show')
        list_parser.add_argument('--type', type=str, help='Filter by memory type')
        
        # stats command
        subparsers.add_parser('stats', help='Show memory statistics')
        
        # doctor command
        subparsers.add_parser('doctor', help='Run diagnostics')
        
        # version command
        subparsers.add_parser('version', help='Show version information')
        
        # help command
        subparsers.add_parser('help', help='Show help message')

        # serve command
        serve_parser = subparsers.add_parser('serve', help='Start MCP HTTP/SSE server')
        serve_parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind')
        serve_parser.add_argument('--port', type=int, default=8765, help='Port to listen')
        serve_parser.add_argument('--api-key', type=str, help='API key for authentication')

        # init-integration command
        integ_parser = subparsers.add_parser('init-integration', help='Initialize AI tool integration')
        integ_parser.add_argument('--tool', type=str, choices=['claude-code', 'cursor', 'all'], default='all', help='Target tool')
        
        if len(args) == 0:
            self.show_welcome()
            return
        
        parsed_args = parser.parse_args(args)
        
        if parsed_args.command == 'init':
            self.cmd_init()
        elif parsed_args.command == 'list':
            self.cmd_list(parsed_args.limit, parsed_args.type)
        elif parsed_args.command == 'stats':
            self.cmd_stats()
        elif parsed_args.command == 'doctor':
            self.cmd_doctor()
        elif parsed_args.command == 'version':
            self.cmd_version()
        elif parsed_args.command == 'help':
            parser.print_help()
        elif parsed_args.command == 'serve':
            self.cmd_serve(parsed_args.host, parsed_args.port, parsed_args.api_key)
        elif parsed_args.command == 'init-integration':
            self.cmd_init_integration(parsed_args.tool)
        else:
            parser.print_help()
    
    def show_welcome(self):
        """Show welcome message."""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🧠 CarryMem - Your Portable AI Memory Layer               ║
║                                                              ║
║   AI remembers you. Not the other way around.               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Quick Start:
  carrymem init       - Set up CarryMem (first time)
  carrymem list       - View your memories
  carrymem stats      - See statistics
  carrymem doctor     - Check system health
  carrymem help       - Show all commands

Documentation: https://github.com/lulin70/memory-classification-engine
""")
    
    def cmd_init(self):
        """Initialize CarryMem configuration."""
        print("🚀 Initializing CarryMem...\n")
        
        # Create config directory
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
            print(f"✅ Created config directory: {self.config_dir}")
        else:
            print(f"ℹ️  Config directory exists: {self.config_dir}")
        
        # Create default config
        if not self.config_file.exists():
            config = {
                "version": __version__,
                "db_path": str(self.db_path),
                "namespace": "default",
                "max_content_length": 50000,
                "max_message_history": 1000
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Created config file: {self.config_file}")
        else:
            print(f"ℹ️  Config file exists: {self.config_file}")
        
        # Initialize database
        try:
            cm = CarryMem(db_path=str(self.db_path))
            print(f"✅ Initialized database: {self.db_path}")
            
            # Test storage
            cm.classify_and_remember("CarryMem initialized successfully!")
            print("✅ Test memory stored")
            
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
            return
        
        print(f"\n🎉 CarryMem is ready to use!\n")
        print("Next steps:")
        print("  1. Try: carrymem stats")
        print("  2. Read: https://github.com/lulin70/memory-classification-engine")
        print("  3. Code: from memory_classification_engine import CarryMem\n")
    
    def cmd_list(self, limit: int = 10, memory_type: Optional[str] = None):
        """List memories."""
        try:
            cm = CarryMem(db_path=str(self.db_path))
            
            # Get memories
            filters = {}
            if memory_type:
                filters['type'] = memory_type
            
            memories = cm.recall_memories(query="", filters=filters, limit=limit)
            
            if not memories:
                print("📭 No memories found")
                print("\n💡 Tip: Store your first memory with:")
                print('   cm = CarryMem()')
                print('   cm.classify_and_remember("I prefer dark mode")')
                return
            
            print(f"\n📚 Your Memories (showing {len(memories)}):\n")
            
            for i, mem in enumerate(memories, 1):
                print(f"{i}. [{mem.get('type', 'unknown')}] {mem.get('content', '')[:80]}")
                print(f"   Confidence: {mem.get('confidence', 0):.2f} | {mem.get('timestamp', 'N/A')}")
                print()
            
        except Exception as e:
            print(f"❌ Error listing memories: {e}")
            print("\n💡 Try running: carrymem doctor")
    
    def cmd_stats(self):
        """Show statistics."""
        try:
            cm = CarryMem(db_path=str(self.db_path))
            stats = cm.get_stats()
            
            print("\n📊 Memory Statistics:\n")
            print(f"Total Memories: {stats.get('total_count', 0)}")
            print(f"\nBy Type:")
            for mem_type, count in stats.get('by_type', {}).items():
                print(f"  • {mem_type}: {count}")
            
            print(f"\nBy Tier:")
            for tier, count in stats.get('by_tier', {}).items():
                print(f"  • Tier {tier}: {count}")
            
            print(f"\nAverage Confidence: {stats.get('avg_confidence', 0):.2f}")
            print()
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            print("\n💡 Try running: carrymem doctor")
    
    def cmd_doctor(self):
        """Run diagnostics."""
        print("\n🔍 Running CarryMem Diagnostics...\n")
        
        issues = []
        
        # Check config directory
        if self.config_dir.exists():
            print(f"✅ Config directory: {self.config_dir}")
        else:
            print(f"❌ Config directory missing: {self.config_dir}")
            issues.append("Config directory not found")
        
        # Check config file
        if self.config_file.exists():
            print(f"✅ Config file: {self.config_file}")
        else:
            print(f"⚠️  Config file missing: {self.config_file}")
            issues.append("Config file not found")
        
        # Check database
        if self.db_path.exists():
            print(f"✅ Database: {self.db_path}")
            size_mb = self.db_path.stat().st_size / (1024 * 1024)
            print(f"   Size: {size_mb:.2f} MB")
        else:
            print(f"⚠️  Database not found: {self.db_path}")
            issues.append("Database not initialized")
        
        # Check permissions
        try:
            test_file = self.config_dir / ".test"
            test_file.touch()
            test_file.unlink()
            print(f"✅ Write permissions: OK")
        except Exception as e:
            print(f"❌ Write permissions: FAILED")
            issues.append(f"Permission error: {e}")
        
        # Try to connect
        try:
            cm = CarryMem(db_path=str(self.db_path))
            print(f"✅ Database connection: OK")
        except Exception as e:
            print(f"❌ Database connection: FAILED")
            issues.append(f"Connection error: {e}")
        
        # Summary
        print()
        if issues:
            print("⚠️  Issues Found:")
            for issue in issues:
                print(f"   • {issue}")
            print("\n💡 Solution: Run 'carrymem init' to fix issues")
        else:
            print("🎉 All checks passed! CarryMem is healthy.")
        print()
    
    def cmd_version(self):
        """Show version information."""
        print(f"\nCarryMem v{__version__}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Config: {self.config_dir}")
        print()

    def cmd_serve(self, host: str, port: int, api_key: str = None):
        """Start MCP HTTP/SSE server."""
        from memory_classification_engine.integration.layer2_mcp.http_server import run_http_server
        print(f"\nStarting CarryMem MCP HTTP Server...")
        print(f"  Host: {host}")
        print(f"  Port: {port}")
        print(f"  SSE endpoint: http://{host}:{port}/sse")
        print(f"  Message endpoint: http://{host}:{port}/message")
        print(f"  Health check: http://{host}:{port}/health")
        print()
        run_http_server(host=host, port=port, api_key=api_key)

    def cmd_init_integration(self, tool: str):
        """Initialize AI tool integration configuration."""
        import shutil
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(pkg_dir))

        if tool in ("claude-code", "all"):
            src = os.path.join(project_root, "integrations", "claude_code", "mcp.json")
            dst_dir = os.path.join(os.getcwd(), ".claude")
            if os.path.exists(src):
                os.makedirs(dst_dir, exist_ok=True)
                shutil.copy2(src, os.path.join(dst_dir, "mcp.json"))
                print(f"Claude Code configuration written to {dst_dir}/mcp.json")
            else:
                config = {
                    "mcpServers": {
                        "carrymem": {
                            "command": "python",
                            "args": ["-m", "memory_classification_engine.integration.layer2_mcp"],
                        }
                    }
                }
                os.makedirs(dst_dir, exist_ok=True)
                with open(os.path.join(dst_dir, "mcp.json"), "w") as f:
                    json.dump(config, f, indent=2)
                print(f"Claude Code configuration written to {dst_dir}/mcp.json")

        if tool in ("cursor", "all"):
            src = os.path.join(project_root, "integrations", "cursor", "mcp.json")
            dst_dir = os.path.join(os.getcwd(), ".cursor")
            if os.path.exists(src):
                os.makedirs(dst_dir, exist_ok=True)
                shutil.copy2(src, os.path.join(dst_dir, "mcp.json"))
                print(f"Cursor configuration written to {dst_dir}/mcp.json")
            else:
                config = {
                    "mcpServers": {
                        "carrymem": {
                            "command": "python",
                            "args": ["-m", "memory_classification_engine.integration.layer2_mcp"],
                        }
                    }
                }
                os.makedirs(dst_dir, exist_ok=True)
                with open(os.path.join(dst_dir, "mcp.json"), "w") as f:
                    json.dump(config, f, indent=2)
                print(f"Cursor configuration written to {dst_dir}/mcp.json")


def main():
    """Main entry point."""
    cli = CarryMemCLI()
    cli.run(sys.argv[1:])


if __name__ == '__main__':
    main()
