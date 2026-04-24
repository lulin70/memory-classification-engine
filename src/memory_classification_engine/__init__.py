"""CarryMem — 随身记忆库. 让 AI Agent 记住用户.

CarryMem = MCE 分类引擎（核心壁垒）+ SQLite 默认存储（开箱即用）+ 可替换适配器（你的选择）

v0.4.0: Semantic recall with synonym expansion, spell correction, cross-language mapping

Quick Start:
    from memory_classification_engine import CarryMem

    cm = CarryMem()
    result = cm.classify_and_remember("I prefer dark mode")
    memories = cm.recall_memories("dark mode")  # Also finds "深色模式", "ダークモード", etc.
"""

from memory_classification_engine.carrymem import CarryMem, StorageNotConfiguredError, KnowledgeNotConfiguredError
from memory_classification_engine.engine import MemoryClassificationEngine
from memory_classification_engine.adapters.base import MemoryEntry, StorageAdapter, StoredMemory
from memory_classification_engine.adapters.sqlite_adapter import SQLiteAdapter
from memory_classification_engine.adapters.obsidian_adapter import ObsidianAdapter

try:
    from memory_classification_engine.semantic.expander import SemanticExpander
    from memory_classification_engine.semantic.merger import ResultMerger
except ImportError:
    SemanticExpander = None
    ResultMerger = None

from memory_classification_engine.__version__ import __version__

__all__ = [
    "CarryMem",
    "MemoryClassificationEngine",
    "MemoryEntry",
    "StorageAdapter",
    "StoredMemory",
    "SQLiteAdapter",
    "ObsidianAdapter",
    "StorageNotConfiguredError",
    "KnowledgeNotConfiguredError",
    # v0.4.0 semantic recall (optional)
    "SemanticExpander",
    "ResultMerger",
]
