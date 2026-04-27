"""CarryMem — Your Portable AI Memory Layer.

CarryMem = MCE Classification Engine + SQLite Default Storage + Replaceable Adapters

v0.8.0: Enhanced CLI, TUI, MCP setup, carrymem doctor, quality management

Quick Start:
    from memory_classification_engine import CarryMem

    cm = CarryMem()
    result = cm.classify_and_remember("I prefer dark mode")
    memories = cm.recall_memories("dark mode")  # Also finds "深色模式", "ダークモード", etc.

CLI:
    carrymem add "I prefer dark mode"
    carrymem list
    carrymem search "theme"
    carrymem setup-mcp --tool cursor
    carrymem doctor
"""

from memory_classification_engine.carrymem import CarryMem, StorageNotConfiguredError, KnowledgeNotConfiguredError
from memory_classification_engine.engine import MemoryClassificationEngine
from memory_classification_engine.adapters.base import MemoryEntry, StorageAdapter, StoredMemory
from memory_classification_engine.adapters.sqlite_adapter import SQLiteAdapter
from memory_classification_engine.adapters.obsidian_adapter import ObsidianAdapter
from memory_classification_engine.adapters.json_adapter import JSONAdapter

try:
    from memory_classification_engine.semantic.expander import SemanticExpander
    from memory_classification_engine.semantic.merger import ResultMerger
except ImportError:
    SemanticExpander = None
    ResultMerger = None

# v0.5.0 security module
try:
    from memory_classification_engine.security import (
        InputValidator,
        ValidationError,
        validate_content,
        validate_query,
        validate_namespace,
    )
except ImportError:
    InputValidator = None
    ValidationError = None
    validate_content = None
    validate_query = None
    validate_namespace = None

try:
    from memory_classification_engine.async_carrymem import AsyncCarryMem
except ImportError:
    AsyncCarryMem = None

from memory_classification_engine.__version__ import __version__

__all__ = [
    "CarryMem",
    "MemoryClassificationEngine",
    "MemoryEntry",
    "StorageAdapter",
    "StoredMemory",
    "SQLiteAdapter",
    "ObsidianAdapter",
    "JSONAdapter",
    "StorageNotConfiguredError",
    "KnowledgeNotConfiguredError",
    "SemanticExpander",
    "ResultMerger",
    "InputValidator",
    "ValidationError",
    "validate_content",
    "validate_query",
    "validate_namespace",
    "AsyncCarryMem",
]
