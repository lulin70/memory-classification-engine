# CarryMem v0.1.2 — 用户视角全面审查报告

> **审查方**: 产品经理 + 架构师 + 测试专家  
> **日期**: 2026-04-23  
> **版本**: v0.1.2  

---

## 一、问题总览

| # | 问题 | 严重度 | 状态 | 影响 |
|---|------|--------|------|------|
| BUG-1 | 中文召回失败 | 🔴 P0 | ✅ 已修复 | TRAE中文环境不可用 |
| BUG-2 | README API 与代码不一致 | 🟡 P1 | ⚠️ 部分修复 | 用户按文档集成会报错 |
| WARN-1 | 配置文件缺失报错刷屏 | 🟡 P1 | ❌ 未修复 | 每次import都打印2行错误 |
| WARN-2 | MCP TOOLS 格式问题 | 🟢 P2 | ❌ 未确认 | 文档与实现不一致 |
| NEW-1 | 缺少默认配置文件 | 🟡 P1 | ❌ 未修复 | 新用户首次使用体验差 |
| NEW-2 | __init__.py 导出过多内部模块 | 🟡 P1 | ❌ 未修复 | 用户看到不相关的导出 |
| NEW-3 | 缺少快速开始验证脚本 | 🟡 P1 | ❌ 未修复 | 用户无法5分钟内验证功能 |
| NEW-4 | MCP Server 无启动参数说明 | 🟢 P2 | ❌ 未修复 | 集成门槛高 |

---

## 二、各角色详细审查

### 👔 产品经理视角

#### 核心痛点：用户从 pip install 到 "能用" 的路径太长

**当前用户体验路径（理想 vs 实际）**：

```
理想: pip install carrymem → 3行代码 → 记忆系统工作 ✅

实际:
  1. pip install carrymem          → OK
  2. from carrymem import ...      → 报错！应该是 memory_classification_engine
  3. cm = CarryMem()               → 打印2行 Error loading config
  4. cm.classify_and_remember(...) → 存储成功
  5. cm.recall_memories("偏好")    → 返回0！❌ (已修复)
```

**问题清单**：

| # | 问题 | 用户感知 | 建议 |
|---|------|---------|------|
| P1 | 包名 `memory_classification_engine` 太长，README 写的是 `from carrymem import` 但实际要 `from memory_classification_engine import` | "文档骗人" | 在 setup.py 中添加 `carrymem` 作为顶层包别名，或明确说明导入方式 |
| P2 | 每次导入都打印 `Error loading config` | "这个库是不是坏了？" | ConfigManager 应该静默处理缺失配置，只在 debug 模式下打印 |
| P3 | README 示例中 `declare_preference(key, value)` 不存在 | "按文档写的代码报 AttributeError" | 统一 API 文档与代码，或添加 alias |
| P4 | 没有 "5分钟验证" 脚本 | "装好了不知道怎么验证" | 提供 `python -m carrymem demo` 一键验证 |
| P5 | MCP 配置需要用户自己写 JSON | "怎么接入 Trae？" | 提供 `.trae/mcp.json` 模板文件 |

#### 架构师视角

#### 核心痛点：公开 API 不稳定，内部实现泄漏到用户空间

**问题清单**：

| # | 问题 | 技术影响 | 建议 |
|---|------|---------|------|
| A1 | `__init__.py` 导出了 `ConfigManager`, `generate_memory_id`, `get_current_time` 等20+ 内部符号 | 用户误用内部API，后续重构会破坏用户代码 | 只导出公共 API: CarryMem, MemoryEntry, StorageAdapter, adapters 子模块 |
| A2 | `CarryMem.storage` 属性不存在（实际是 `.adapter`） | 属性名不一致增加认知负担 | 添加 `storage` 作为 `adapter` 的 property alias |
| A3 | `declare_preference(key, value)` 在 README 中但代码是 `declare(message)` | API 设计不一致 | 决定最终 API 并统一 |
| A4 | ConfigManager 从固定路径 `./config/` 读配置 | 不可移植，不同 cwd 会找不到配置 | 改为从包内置数据或 ~/.carrymem/config.yaml |
| A5 | FTS tokenizer 迁移逻辑可能对已有数据库无效 | 旧数据库升级后索引可能不完整 | 在迁移后触发一次全量 rebuild |

#### 测试专家视角

#### 核心痛点：测试覆盖了"happy path"，缺少"真实用户场景"

**现有测试覆盖 vs 缺失**：

| 场景 | 已覆盖 | 缺失 |
|------|--------|------|
| 英文分类+存储+召回 | ✅ | |
| 中文分类+存储+召回 | ✅ | |
| 日语分类+存储+召回 | ✅ | |
| declare() | ✅ | |
| get_profile() | ✅ | |
| build_system_prompt() | ✅ | |
| export/import | ✅ | |
| Namespace 隔离 | ✅ | |
| Plugin 加载 | ✅ | |
| **首次安装体验（pip install 后）** | ❌ | **关键缺失** |
| **ConfigManager 缺失配置时的行为** | ❌ | **关键缺失** |
| **MCP Server 实际启动和工具调用** | ❌ | **缺失** |
| **大容量存储（1000+条记忆）的召回性能** | ❌ | **缺失** |
| **并发写入安全性** | ❌ | **缺失** |
| **数据库损坏恢复** | ❌ | **缺失** |

---

## 三、优先修复建议（按用户影响排序）

### P0 — 必须立即修复（阻塞用户使用）

1. **消除 config 缺失报错** — ConfigManager 静默处理，不打印 Error
2. **清理 __init__.py 导出** — 只导出公共 API
3. **添加 storage 属性 alias** — `cm.storage` 可用

### P1 — 本周内修复（改善用户体验）

4. **统一 README API 文档** — 所有示例代码可运行
5. **提供默认配置文件** — 首次运行自动生成
6. **提供 demo 验证命令** — `python -m carrymem demo`
7. **提供 .trae/mcp.json 模板**

### P2 — 下个版本（锦上添花）

8. MCP Server 启动文档完善
9. 性能基准测试（大容量）
10. 并发安全测试

---

*本报告由 PM/ARCH/QA 三角色联合审查生成*
