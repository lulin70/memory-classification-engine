"""CarryMem — 随身记忆库. 让 AI Agent 记住用户.

CarryMem = MCE 分类引擎（核心壁垒）+ SQLite 默认存储（开箱即用）+ 可替换适配器（你的选择）
"""

from memory_classification_engine.engine import MemoryClassificationEngine
from memory_classification_engine.carrymem import CarryMem, StorageNotConfiguredError, KnowledgeNotConfiguredError
from memory_classification_engine.adapters.base import MemoryEntry, StorageAdapter, StoredMemory
from memory_classification_engine.adapters.sqlite_adapter import SQLiteAdapter
from memory_classification_engine.adapters.obsidian_adapter import ObsidianAdapter
from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.utils.helpers import (
    generate_memory_id,
    get_current_time,
    extract_content,
)
from memory_classification_engine.utils.logger import logger

__version__ = "0.7.0"
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
    "ConfigManager",
    "generate_memory_id",
    "get_current_time",
    "extract_content",
    "logger",
]
