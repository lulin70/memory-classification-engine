#!/usr/bin/env python3
"""
CarryMem CLI Enhancements
增强的 CLI 命令实现：doctor, status, 改进的 setup-mcp
"""

import sys
import os
import json
import sqlite3
import shutil
from pathlib import Path
from typing import Optional, List, Tuple

try:
    from memory_classification_engine import CarryMem
    from memory_classification_engine.__version__ import __version__
except ImportError:
    print("Error: CarryMem not properly installed")
    sys.exit(1)


_DEFAULT_DB = Path.home() / ".carrymem" / "memories.db"
_HAS_COLOR = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    if not _HAS_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def _green(t): return _c("32", t)
def _red(t): return _c("31", t)
def _yellow(t): return _c("33", t)
def _cyan(t): return _c("36", t)
def _dim(t): return _c("2", t)
def _bold(t): return _c("1", t)


# ============================================================================
# Doctor Command - 系统诊断
# ============================================================================

def cmd_doctor(args):
    """Run system diagnostics"""
    print("🔍 Checking CarryMem health...")
    print("")
    
    issues = []
    warnings = []
    
    # 1. 检查 Python 版本
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 9):
        print(f"✅ Python version: {py_version}")
    else:
        print(f"❌ Python version: {py_version} (需要 3.9+)")
        issues.append("Python 版本过低")
    
    # 2. 检查命令可用性
    if shutil.which("carrymem"):
        print("✅ Command 'carrymem' is available")
    else:
        print("⚠️  Command 'carrymem' not in PATH")
        warnings.append("全局命令不可用")
    
    # 3. 检查数据库
    db_path = _DEFAULT_DB
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memories")
            count = cursor.fetchone()[0]
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"✅ Database: {db_path}")
            print(f"   ({count} memories, {size_mb:.1f} MB)")
            conn.close()
        except Exception as e:
            print(f"❌ Database error: {e}")
            issues.append("数据库损坏")
    else:
        print(f"⚠️  Database not found: {db_path}")
        warnings.append("数据库未初始化")
    
    # 4. 检查 MCP 配置
    claude_config = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    if claude_config.exists():
        try:
            with open(claude_config) as f:
                config = json.load(f)
            if "carrymem" in config.get("mcpServers", {}):
                print("✅ MCP config: Found in Claude Desktop")
            else:
                print("⚠️  MCP ig: Not configured in Claude Desktop")
                warnings.append("MCP 未配置")
        except Exception as e:
            print(f"⚠️  MCP config: Error reading ({e})")
    else:
        print("ℹ️  Claude Desktop not detected")
    
    # 5. 检查依赖包
    try:
        import yaml
        print("✅ PyYAML: Installed")
    except ImportError:
        print("⚠️  PyYAML: Not installed")
        warnings.append("PyYAML 未安装")
    
    try:
        import textual
        print("✅ Textual: Installed (TUI available)")
    except ImportError:
        print("ℹ️  Textual: Not installed (TUI unavailable)")
    
    print("")
    print("=" * 50)
    
    # 总结
    if issues:
        print(f"❌ Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"   - {issue}")
    
    if warnings:
        print(f"⚠️  Found {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"   - {warning}")
    
    if not issues and not warnings:
        print("✅ All checks passed! CarryMem is healthy.")
    
    # 修复建议
    if issues or warnings:
        print("")
        print("💡 Suggested fixes:")
        if "Python 版本过低" in issues:
            print("   - Upgrade Python: brew install python@3.11")
        if "全局命令不可用" in warnings:
            print("   - Run: pip uninstall carrymem -y && pip install -e .")
            print("   - Or add to PATH: export PATH=\"$PATH:$(python3 -m site --user-base)/bin\"")
        if "数据库未初始化" in warnings:
            print("   - Run: python3 -m memory_classification_engine.cli init")
        if "数据库损坏" in issues:
            print("   - Backup: cp ~/.carrymem/memories.db ~/.carrymem/memories.db.backup")
            print("   -rm ~/.carrymem/memories.db && carrymem init")
        if "MCP 未配置" in warnings:
            print("   - Run: python3 -m memory_classification_engine.cli_enhancements setup-mcp --tool claude")
        if "PyYAML 未安装" in warnings:
            print("   - Run: pip install PyYAML")
    
    print("")
    return 0 if not issues else 1


# ============================================================================
# Status Command - 系统状态
# ============================================================================

def cmd_status(args):
    """Show system status"""
    print("📊 CarryMem Status")
    print("=" * 50)
    print("")
    
    # 1. 数据库信息
    db_path = _DEFAULT_DB
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"💾 Database: {db_path}")
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # 总记忆数
            cursor.execute("SELECT COUNT(*) FROM memories")
            total = cursor.fetchone()[0]
            print(f"📝 Memories: {total} items ({size_mb:.1f} MB)")
            
            # 按类型统计
            cursor.execute("SELECT type, COUNT(*) FROM memories GROUP BY TYPE ORDER BY COUNT(*) DESC")
            types = cursor.fetchall()
            if types:
                print("")
                print("📊 By Type:")
                for mem_type, count in types:
                    print(f"   - {mem_type}: {count}")
            
            # 按命名空间统计
            cursor.execute("SELECT namespace, COUNT(*) FROM memories GROUP BY namespace")
            namespaces = cursor.fetchall()
            if len(namespaces) > 1 or (namespaces and namespaces[0][0] != "default"):
                print("")
                print("🏷️  Namespaces:")
                for ns, count in namespaces:
                    print(f"   - {ns}: {count}")
            
            conn.close()
        except Exception as e:
            print(f"⚠️  Error reading database: {e}")
    else:
        print(f"⚠️  Database not found: {db_path}")
        print("💡 Run: carrymem init")
        return 1
    
    # 2. MCP 状态
    print("")
    print("🔌 MCP Status:")
    
    claude_config = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    if claude_config.exists():
        try:
            with open(claude_config) as f:
                config = json.load(f)
            if "carrymem" in config.get("mcpServers", {}):
                print("   ✅ Claude Desktop: Configured")
            else:
                print("   ❌ Claude Desktop: Not configured")
        except Exception:
            print("   ⚠️  Claude Desktop: Error reading config")
    else:
        print("   ℹ️  Claude Desktop: Not detected")
    
    # Cursor 配置检测
    cursor_config = Path.home() / ".cursor/mcp_config.json"
    if cursor_config.exists():
        print("   ✅ Cursor: Detected")
    else:
        print("   ℹ️  Cursor: Not detected")
    
    # 3. 最近活动
    print("")
    print("🎯 Recent Activity:")
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT content, created_at FROM memories ORDER BY created_at DESC LIMIT 3")
        recent = cursor.fetchall()
        if recent:
            for content, created_at in recent:
                content_short = content[:50] + "..." if len(content) > 50 else content
                print(f"   - {content_short}")
        else:
            print("   (No recent activity)")
        conn.close()
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    print("")
    return 0


# ============================================================================
# Setup MCP Command - MCP 配置
# ============================================================================

def cmd_setup_mcp(args):
    """Configure MCP integration"""
    # 解析参数
    tool = None
    for i, arg in enumerate(args):
        if arg == "--tool" and i + 1 < len(args):
            tool = args[i + 1]
            break
    
    if not tool:
        tool = "auto"
    
    print("🔌 Setting up MCP integration...")
    print("")
    
    if tool == "auto":
        # 自动检测
        detected = []
        
        claude_config = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
        if claude_config.exists():
            detected.append(("claude", claude_config))
        
        cursor_config = Path.home() / ".cursor/mcp_config.json"
        if cursor_config.exists():
            detected.append(("cursor", cursor_config))
        
        if not detected:
            print("⚠️  No supported tools detected")
            print("")
            print("Supported tools:")
            print("  - Claude Desktop")
            print("  - Cursor")
            print("")
            print("Manual setup:")
            print("  python3 -m memory_classification_engine.cli_enhancements setup-mcp --tool claude")
            print("  python3 -m memory_classification_engine.cli_enhancements setup-mcp --tool cursor")
            return 1
        
        print(f"✅ Detected {len(detected)} tool(s):")
        for tool_name, _ in detected:
            print(f"   - {tool_name}")
        print("")
        
        # 配置所有检测到的工具
        for tool_name, config_path in detected:
            _setup_mcp_for_tool(tool_name, config_path)
    
    else:
        # 指定工具
        config_path = _get_mcp_config_path(tool)
        if not config_path:
            print(f"❌ Unknown tool: {tool}")
            print("Supported: claude, cursor")
            return 1
        
        _setup_mcp_for_tool(tool, config_path)
    
    print("")
    print("✅ MCP setup complete!")
    print("")
    print("Next steps:")
    print("  1. Restart your tool (Claude Desktop/Cursor)")
    print("  2. Verify: python3 -m memory_classification_engine.cli_enhancements status")
    print("")
    return 0


def _get_mcp_config_path(tool: str) -> Optional[Path]:
    """Get MCP config path for tool"""
    if tool == "claude":
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    elif tool == "cursor":
        return Path.home() / ".cursor/mcp_config.json"
    return None


def _setup_mcp_for_tool(tool: str, config_path: Path):
    """Setup MCP for specific tool"""
    print(f"📝 Configuring {tool}...")
    
    # 读取现有配置
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
        except Exception as e:
            print(f"⚠️  Error reading config: {e}")
            config = {}
    else:
        config = {}
        config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 添加 CarryMem 配置
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    config["mcpServers"]["carrymem"] = {
        "command": "python3",
        "args": ["-m", "memory_classification_engine.integration.layer2_mcp"]
    }
    
    # 写入配置
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Updated {config_path}")
    except Exception as e:
        print(f"❌ Error writing config: {e}")
        print("")
        print("Manual setup:")
        print(f"  Edit: {config_path}")
        print('  Add to "mcpServers":')
        print('    "carrymem": {')
        print('      "command": "python3",')
        print('      "args": ["-m", "memory_classification_engine.integration.layer2_mcp"]')
        print('    }')


# ============================================================================
# Main - 用于独立测试
# ============================================================================

def main():
    """Main entry point for testing"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 -m memory_classification_engine.cli_enhancements doctor")
        print("  python3 -m memory_classification_engine.cli_enhancements status")
        print("  python3 -m memory_classification_engine.cli_enhancements setup-mcp --tool claude")
        sys.exit(0)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "doctor":
        sys.exit(cmd_doctor(args))
    elif command == "status":
        sys.exit(cmd_status(args))
    elif command == "setup-mcp":
        sys.exit(cmd_setup_mcp(args))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
