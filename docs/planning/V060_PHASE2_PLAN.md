# Phase 2 实施计划: 安全与可靠性 (v0.6.0)

> **目标**: 用户放心把记忆交给 CarryMem
> **版本**: v0.5.0 → v0.6.0
> **制定日期**: 2026-04-26

---

## 一、实施顺序与依赖关系

```
2.1 数据加密 (核心安全基础)
  ↓
2.2 自动备份 (数据安全)
  ↓
2.3 访问审计 (可追溯性)
  ↓
D-1~D-6 技术债务修复 (代码质量)
  ↓
2.4 测试覆盖率 85%+ (质量保障)
  ↓
2.5 性能基准 (性能验证)
  ↓
2.6 模糊测试 (安全验证)
```

---

## 二、2.1 数据加密

### 设计

使用 Python 标准库 `hashlib` + `hmac` 实现零依赖加密方案。
如果 `cryptography` 库可用，使用 Fernet (AES-128-CBC)；
否则使用 `hashlib.pbkdf2_hmac` + AES-CTR 模式（通过标准库实现）。

**策略**: 加密敏感字段（content, original_message），保留元数据明文用于查询。

```python
class MemoryEncryption:
    """At-rest encryption for memory content."""

    def __init__(self, key: Optional[str] = None):
        # key: 用户提供的密码，或自动生成的密钥
        # 存储位置: ~/.carrymem/.key
        if key:
            self._key = self._derive_key(key)
        else:
            self._key = self._load_or_generate_key()

    def encrypt(self, plaintext: str) -> str:
        # 返回 base64 编码的密文

    def decrypt(self, ciphertext: str) -> str:
        # 返回明文

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        # PBKDF2-HMAC-SHA256, 100000 iterations
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
```

### 集成方式

```python
# SQLiteAdapter 构造函数新增参数
SQLiteAdapter(db_path=..., encryption_key="user_password")

# remember 时: 加密 content + original_message
# recall 时: 解密 content + original_message
# FTS5 搜索: 使用解密后的内容（搜索时临时解密）
# export 时: 可选加密导出
```

### 实现位置
- **新文件**: `src/memory_classification_engine/security/encryption.py`
- **修改**: `sqlite_adapter.py` — 加解密集成
- **修改**: `setup.py` — `extras_require["encryption"]` 添加 cryptography
- **修改**: `carrymem.py` — 构造函数新增 `encryption_key` 参数

### 验收标准
- [ ] 加密后数据库中 content 列为密文
- [ ] recall 返回解密后的明文
- [ ] FTS5 搜索正常工作（搜索时解密）
- [ ] 密钥存储在 ~/.carrymem/.key，权限 600
- [ ] 无 cryptography 库时使用标准库 fallback
- [ ] 密钥错误时抛出明确异常

---

## 三、2.2 自动备份

### 设计

```python
class BackupManager:
    """Automatic backup for CarryMem databases."""

    def __init__(self, db_path: str, backup_dir: Optional[str] = None,
                 max_backups: int = 10, interval_hours: int = 24):
        self._db_path = db_path
        self._backup_dir = backup_dir or os.path.join(os.path.dirname(db_path), "backups")
        self._max_backups = max_backups
        self._interval = interval_hours

    def create_backup(self) -> str:
        """Create a timestamped backup. Returns backup path."""

    def restore_backup(self, backup_path: str) -> None:
        """Restore from a backup file."""

    def list_backups(self) -> List[Dict]:
        """List available backups with metadata."""

    def cleanup_old_backups(self) -> int:
        """Remove backups exceeding max_backups. Returns removed count."""

    def auto_backup_if_needed(self) -> Optional[str]:
        """Create backup if interval has elapsed since last backup."""
```

### 备份策略
- **完整备份**: SQLite `VACUUM INTO` 命令（零停机）
- **命名**: `memories_YYYYMMDD_HHMMSS.db`
- **保留**: 最多 10 个备份，FIFO 淘汰
- **自动触发**: 每次 `remember` 操作后检查间隔（可选）

### 实现位置
- **新文件**: `src/memory_classification_engine/backup.py`
- **修改**: `carrymem.py` — 新增 `backup()` / `restore()` / `list_backups()` 方法

### 验收标准
- [ ] 创建备份文件可被 SQLite 打开
- [ ] 恢复后数据完整
- [ ] 自动清理旧备份
- [ ] 备份目录权限 700

---

## 四、2.3 访问审计

### 设计

```python
class AuditLogger:
    """Structured audit logging for memory operations."""

    def log_operation(
        self,
        operation: str,       # "remember", "recall", "forget", "update", "rollback"
        namespace: str,
        storage_key: Optional[str] = None,
        details: Optional[Dict] = None,
        success: bool = True,
    ) -> None:
        """Log an operation to the audit trail."""
```

### 审计日志 Schema

```sql
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    operation TEXT NOT NULL,
    namespace TEXT NOT NULL,
    storage_key TEXT,
    memory_type TEXT,
    success INTEGER NOT NULL DEFAULT 1,
    details TEXT,
    source TEXT DEFAULT 'api'   -- 'api', 'mcp', 'cli'
);
```

### 实现位置
- **新文件**: `src/memory_classification_engine/security/audit.py`
- **修改**: `sqlite_adapter.py` — 操作时记录审计日志
- **修改**: `carrymem.py` — 新增 `get_audit_log()` 方法

### 验收标准
- [ ] 所有 remember/recall/forget/update 操作记录审计日志
- [ ] 审计日志可查询（按时间、操作类型、namespace）
- [ ] 审计日志不可篡改（只增不改）
- [ ] MCP 操作标记 source='mcp'

---

## 五、技术债务修复 (D-1~D-6)

| 编号 | 债务 | 修复方案 |
|------|------|----------|
| D-1 | test_environment.py / test_execution_context.py 非标准格式 | 重构为 pytest 格式或移至 scripts/ |
| D-2 | 缺少 ObsidianAdapter 功能测试 | 创建 mock vault fixture + 核心功能测试 |
| D-3 | 缺少 CLI 测试 | 使用 capsys/monkeypatch 测试各命令 |
| D-4 | SQL 注入检测误杀正常文本 | 重写 InputValidator，降低误报率 |
| D-5 | 路径遍历检测过于简单 | 使用 os.path.realpath + 前缀检查 |
| D-6 | 两套验证器并存 | 统一为 security/input_validator.py |

---

## 六、2.4 测试覆盖率 85%+

### 当前覆盖缺口

| 模块 | 当前测试 | 需要补充 |
|------|---------|---------|
| ObsidianAdapter | 2 (仅加载) | ~15 (核心功能) |
| CLI | 0 | ~10 (各命令) |
| MCP handlers | 0 | ~8 (handler 测试) |
| 加密 | 0 | ~8 |
| 备份 | 0 | ~6 |
| 审计 | 0 | ~6 |
| InputValidator | 部分 | ~5 (修复后) |

### 目标
- 总测试数: 276 + 58 = **334+**
- 覆盖率: **85%+**

---

## 七、2.5 性能基准

### 测试场景
- 10,000 条记忆的 recall P99 延迟
- 1,000 条记忆的 FTS5 搜索延迟
- 100 条记忆的 remember_batch 延迟
- 缓存命中 vs 未命中延迟对比
- 加密/解密性能开销

### 目标
- P99 recall < 200ms (10K 记忆)
- FTS5 搜索 < 50ms
- 加密开销 < 10%

---

## 八、2.6 模糊测试

### 测试场景
- 随机 Unicode 输入
- 超长字符串 (1MB+)
- 嵌套 JSON 注入
- 路径遍历变体 (%2e%2e, ..../, etc.)
- SQL 注入变体
- 空值/None 注入
- 类型混淆 (int where str expected)

---

## 九、文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `security/encryption.py` | 新建 | 数据加密模块 |
| `backup.py` | 新建 | 自动备份模块 |
| `security/audit.py` | 新建 | 审计日志模块 |
| `sqlite_adapter.py` | 修改 | 加解密 + 审计集成 |
| `carrymem.py` | 修改 | 新增 encryption_key/backup/audit API |
| `security/input_validator.py` | 修改 | 降低误报率 |
| `setup.py` | 修改 | extras_require["encryption"] |
| `test_encryption.py` | 新建 | 加密测试 |
| `test_backup.py` | 新建 | 备份测试 |
| `test_audit.py` | 新建 | 审计测试 |
| `test_obsidian.py` | 新建 | Obsidian 适配器测试 |
| `test_cli.py` | 新建 | CLI 测试 |
| `test_fuzz.py` | 新建 | 模糊测试 |
| `test_performance.py` | 新建 | 性能基准 |
