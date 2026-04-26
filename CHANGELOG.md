# Changelog

All notable changes to CarryMem will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Custom exception classes for better error handling
- Context manager support (`__enter__`/`__exit__`) for proper resource cleanup
- CI/CD pipeline with GitHub Actions
- Type checking configuration with mypy
- Example code demonstrating basic and thread-safe usage
- This CHANGELOG file

### Changed
- **BREAKING**: SQLite adapter now uses ThreadLocal connections for thread safety
- Improved exception handling with specific exception types
- Better resource management with automatic connection cleanup
- `message_history` now uses `deque(maxlen=1000)` instead of unbounded list

### Fixed
- Thread safety issues in SQLiteAdapter (replaced `check_same_thread=False` with ThreadLocal)
- Resource leaks from unclosed database connections
- Potential race conditions in multi-threaded environments
- Memory leak in MemoryClassificationEngine (`message_history` unbounded growth)

### Security
- Fixed potential SQL injection risks in dynamic query construction
- Improved input validation

## [0.4.1] - 2024-XX-XX

### Added
- Composite indexes for common query patterns
- Performance optimizations for recall operations

### Changed
- Improved query performance with better indexing strategy

## [0.4.0] - 2024-XX-XX

### Added
- Semantic recall with synonym expansion
- Spell correction support
- Cross-language mapping
- Result fusion with zero external dependencies

### Changed
- Enhanced FTS5 search with semantic capabilities
- Improved recall accuracy

## [0.3.0] - 2024-XX-XX

### Added
- Namespace support for multi-tenant scenarios
- TTL-based memory expiration
- Batch operations for better performance

### Changed
- Database schema migration for namespace support

## [0.2.0] - 2024-XX-XX

### Added
- FTS5 full-text search
- Content deduplication via content_hash
- Tier-based memory classification

### Changed
- Switched from basic SQLite to FTS5 for better search
\.1.0] - 2024-XX-XX

### Added
- Initial release
- Basic memory storage and recall
- SQLite backend
- Simple classification engine

---

## Migration Guide

### Upgrading to v0.4.2 (Unreleased)

**Thread Safety Improvements:**
- The SQLiteAdapter now uses ThreadLocal connections instead of a single shared connection
- This change is backward compatible but improves thread safety significantly
- If you're using CarryMem in multi-threaded environments, you should see improved stability

**Resource Management:**
- CarryMem and SQLiteAdapter now support context managers
- Recommended usage:
  ```python
  with CarryMem() as cm:
      cm.store("memory")
      results = cm.recall("query")
  # Resources automatically cleaned up
  ```

**Exception Handling:**
- New custom exception classes provide better error information
- Catch specific exceptions instead of generic `Exception`:
  ```python
  from memory_classification_engine.exceptions import DatabaseError, ConnectionError
  
  try:
      cm.store("memory")
  except DatabaseError as e:
      # Handle database-specific errors
      pass
  except ConnectionError as e:
      # Handle connection errors
      pass
  ```

### Upgrading to v0.4.0

**Semantic Recall:**
- Semantic recall is enabled by default
- To disable: `CarryMem(enable_semantic_recall=False)`
- No breaking changes to existing API

### Upgrading to v0.3.0

**Namespace Support:**
- Default namespace is "default"
- Existing data will be migrated automatically
- To use custom namespace: `CarryMem(namespace="my-namespace")`

---

## Support

For issues, questions, or contributions, please visit:
- GitHub Issues: [your-repo-url]/issues
- Documentation: [your-docs-url]
