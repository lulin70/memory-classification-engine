"""
Tests for CLI Enhancements Module
Tests for doctor, status, and setup-mcp commands
"""

import json
import sqlite3
import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest

from memory_classification_engine.cli_enhancements import (
    cmd_doctor,
    cmd_status,
    cmd_setup_mcp,
    _get_mcp_config_path,
    _setup_mcp_for_tool,
)


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary test database"""
    db_path = tmp_path / "test_memories.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE memories (
            id INTEGER PRIMARY KEY,
            content TEXT,
            type TEXT,
            namespace TEXT DEFAULT 'default',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def populated_db(temp_db):
    """Create a database with test data"""
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    
    test_data = [
        ("I prefer dark mode", "preference", "default"),
        ("Python is my main language", "fact", "default"),
        ("Meeting at 3pm tomorrow", "event", "work"),
        ("Use TDD for all projects", "guideline", "work"),
    ]
    
    for content, mem_type, namespace in test_data:
        cursor.execute(
            "INSERT INTO memories (content, type, namespace) VALUES (?, ?, ?)",
            (content, mem_type, namespace)
        )
    
    conn.commit()
    conn.close()
    return temp_db


class TestCmdDoctor:
    """Tests for cmd_doctor function"""
    
    def test_doctor_healthy_system(self, temp_db, capsys, monkeypatch):
        """Test doctor command with all checks passing"""
        monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/carrymem")
        monkeypatch.setattr(
            "memory_classification_engine.cli_enhancements._DEFAULT_DB",
            temp_db
        )
        
        result = cmd_doctor([])
        
        captured = capsys.readouterr()
        assert "Checking" in captured.out
        assert "health" in captured.out
        assert "Python version" in captured.out
        assert "Command 'carrymem' is available" in captured.out
        assert "Database" in captured.out
    
    def test_doctor_missing_database(self, tmp_path, capsys, monkeypatch):
        """Test doctor command when database doesn't exist"""
        non_existent_db = tmp_path / "nonexistent.db"
        monkeypatch.setattr(
            "memory_classification_engine.cli_enhancements._DEFAULT_DB",
            non_existent_db
        )
        monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/carrymem")
        
        result = cmd_doctor([])
        
        captured = capsys.readouterr()
        assert "Database not found" in captured.out
        assert "Database not initialized" in captured.out
        assert "cli init" in captured.out
    
    def test_doctor_command_not_in_path(self, temp_db, capsys, monkeypatch):
        """Test doctor command when carrymem not in PATH"""
        monkeypatch.setattr("shutil.which", lambda x: None)
        monkeypatch.setattr(
            "memory_classification_engine.cli_enhancements._DEFAULT_DB",
            temp_db
        )
        
        result = cmd_doctor([])
        
        captured = capsys.readouterr()
        assert "Command 'carrymem' not in PATH" in captured.out
        assert "Global command not available" in captured.out


class TestCmdStatus:
    """Tests for cmd_status function"""
    
    def test_status_with_memories(self, populated_db, capsys, monkeypatch):
        """Test status command with populated database"""
        monkeypatch.setattr(
            "memory_classification_engine.cli_enhancements._DEFAULT_DB",
            populated_db
        )
        
        result = cmd_status([])
        
        captured = capsys.readouterr()
        assert result == 0
        assert "CarryMem Status" in captured.out
        assert "4 items" in captured.out
        assert "By Type:" in captured.out
        assert "Namespaces:" in captured.out
        assert "work" in captured.out
    
    def test_status_empty_database(self, temp_db, capsys, monkeypatch):
        """Test status command with empty database"""
        monkeypatch.setattr(
            "memory_classification_engine.cli_enhancements._DEFAULT_DB",
            temp_db
        )
        
        result = cmd_status([])
        
        captured = capsys.readouterr()
        assert result == 0
        assert "0 items" in captured.out
        assert "No recent activity" in captured.out
    
    def test_status_missing_database(self, tmp_path, capsys, monkeypatch):
        """Test status command when database doesn't exist"""
        non_existent_db = tmp_path / "nonexistent.db"
        monkeypatch.setattr(
            "memory_classification_engine.cli_enhancements._DEFAULT_DB",
            non_existent_db
        )
        
        result = cmd_status([])
        
        captured = capsys.readouterr()
        assert result == 1
        assert "Database not found" in captured.out
        assert "carrymem init" in captured.out
    
    def test_status_shows_recent_activity(self, populated_db, capsys, monkeypatch):
        """Test that status shows recent memories"""
        monkeypatch.setattr(
            "memory_classification_engine.cli_enhancements._DEFAULT_DB",
            populated_db
        )
        
        result = cmd_status([])
        
        captured = capsys.readouterr()
        assert "Recent Activity:" in captured.out


class TestCmdSetupMcp:
    """Tests for cmd_setup_mcp function"""
    
    def test_setup_mcp_claude(self, tmp_path, capsys, monkeypatch):
        """Test MCP setup for Claude Desktop"""
        config_dir = tmp_path / "Library/Application Support/Claude"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "claude_desktop_config.json"
        config_path.write_text(json.dumps({}))
        
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        
        result = cmd_setup_mcp(["--tool", "claude"])
        
        captured = capsys.readouterr()
        assert result == 0
        assert "Setting up MCP integration" in captured.out
        assert "Configuring" in captured.out
        assert "MCP setup complete" in captured.out
        
        with open(config_path) as f:
            config = json.load(f)
        assert "mcpServers" in config
        assert "carrymem" in config["mcpServers"]
        assert config["mcpServers"]["carrymem"]["command"] == "python3"
    
    def test_setup_mcp_cursor(self, tmp_path, capsys, monkeypatch):
        """Test MCP setup for Cursor"""
        config_dir = tmp_path / ".cursor"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "mcp_config.json"
        config_path.write_text(json.dumps({}))
        
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        
        result = cmd_setup_mcp(["--tool", "cursor"])
        
        captured = capsys.readouterr()
        assert result == 0
        assert "Configuring cursor" in captured.out
        
        with open(config_path) as f:
            config = json.load(f)
        assert "carrymem" in config["mcpServers"]
    
    def test_setup_mcp_auto_detect(self, tmp_path, capsys, monkeypatch):
        """Test MCP setup with auto-detection"""
        claude_dir = tmp_path / "Library/Application Support/Claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "claude_desktop_config.json").write_text(json.dumps({}))
        
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir(parents=True)
        (cursor_dir / "mcp_config.json").write_text(json.dumps({}))
        
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        
        result = cmd_setup_mcp([])
        
        captured = capsys.readouterr()
        assert result == 0
        assert "Detected 2 tool(s)" in captured.out
        assert "claude" in captured.out
        assert "cursor" in captured.out
    
    def test_setup_mcp_no_tools_found(self, tmp_path, capsys, monkeypatch):
        """Test MCP setup when no tools detected"""
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        
        result = cmd_setup_mcp([])
        
        captured = capsys.readouterr()
        assert result == 1
        assert "No supported tools detected" in captured.out
        assert "Claude Desktop" in captured.out
        assert "Cursor" in captured.out
    
    def test_setup_mcp_unknown_tool(self, capsys):
        """Test MCP setup with unknown tool"""
        result = cmd_setup_mcp(["--tool", "unknown"])
        
        captured = capsys.readouterr()
        assert result == 1
        assert "Unknown tool: unknown" in captured.out


class TestHelperFunctions:
    """Tests for helper functions"""
    
    def test_get_mcp_config_path_claude(self, tmp_path, monkeypatch):
        """Test config path detection for Claude"""
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        
        path = _get_mcp_config_path("claude")
        
        assert path is not None
        assert "Claude" in str(path)
        assert "claude_desktop_config.json" in str(path)
    
    def test_get_mcp_config_path_cursor(self, tmp_path, monkeypatch):
        """Test config path detection for Cursor"""
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        
        path = _get_mcp_config_path("cursor")
        
        assert path is not None
        assert ".cursor" in str(path)
        assert "mcp_config.json" in str(path)
    
    def test_get_mcp_config_path_unknown(self):
        """Test config path detection for unknown tool"""
        path = _get_mcp_config_path("unknown")
        assert path is None
    
    def test_setup_mcp_for_tool_new_config(self, tmp_path, capsys):
        """Test creating new MCP configuration"""
        config_path = tmp_path / "test_config.json"
        
        _setup_mcp_for_tool("test", config_path)
        
        captured = capsys.readouterr()
        assert "Configuring test" in captured.out
        assert "Updated" in captured.out
        
        assert config_path.exists()
        with open(config_path) as f:
            config = json.load(f)
        assert "mcpServers" in config
        assert "carrymem" in config["mcpServers"]
    
    def test_setup_mcp_for_tool_existing_config(self, tmp_path, capsys):
        """Test updating existing MCP configuration"""
        config_path = tmp_path / "test_config.json"
        
        existing_config = {
            "mcpServers": {
                "other_server": {
                    "command": "node",
                    "args": ["server.js"]
                }
            }
        }
        config_path.write_text(json.dumps(existing_config))
        
        _setup_mcp_for_tool("test", config_path)
        
        with open(config_path) as f:
            config = json.load(f)
        assert "other_server" in config["mcpServers"]
        assert "carrymem" in config["mcpServers"]
        assert len(config["mcpServers"]) == 2
