# CarryMem 文档中心

**版本**: v0.2.0  
**最后更新**: 2026-04-27

---

## 🚀 快速开始（新用户必读）

### 1. 安装指南
- **[一键安装](../install.sh)** - 推荐！自动安装和配置
- **[快速开始指南](QUICK_START_GUIDE.md)** - 5分钟上手

### 2. 基础使用
```bash
# 安装
bash install.sh

# 初始化
carrymem init

# 添加记忆
carrymem add "I prefer dark mode"

# 搜索记忆
carrymem search "theme"

# 查看状态
carrymem status
```

---

## 📚 核心文档

### 用户文档

| 文档 | 说明 | 适用人群 |
|------|------|---------|
| [快速修复指南](QUICK_FIX_GUIDE.md) | 常见问题快速解决 | ⭐ 所有用户 |
| [故障排除](TROUBLESHOOTING.md) | 10个常见问题详解 | ⭐ 所有用户 |
| [CLI增强功能指南](CLI_ENHANCEMENTS_GUIDE.md) | doctor/status/setup-mcp命令 | ⭐ 所有用户 |
| [用户故事](USER_STORIES.md) | 实际使用场景 | 新用户 |

### 开发者文档

| 文档 | 说明 | 适用人群 |
|------|------|---------|
| [架构文档](ARCHITECTURE.md) | 系统架构设计 | 开发者 |
| [API参考](API_REFERENCE.md) | API接口文档 | 开发者 |
| [路线图](ROADMAP.md) | 未来规划 | 贡献者 |

### 评估报告（内部参考）

| 文档 | 说明 | 用途 |
|------|------|------|
| [用户可用性评估](USER_READINESS_ASSESSMENT.md) | 实际测试结果 | 内部参考 |
| [优化建议](OPTIMIZATION_RECOMMENDATIONS.md) | 15项改进建议 | 内部参考 |
| [实施总结](IMPLEMENTATION_SUMMARY.md) | 已完成工作 | 内部参考 |

---

## 🛠️ 新功能（v0.2.0）

### 1. 系统诊断命令
```bash
carrymem doctor
# 或
python3 -m memory_classification_engine.cli_enhancements doctor
```
自动检查：
- ✅ Python版本
- ✅ 数据库状态
- ✅ MCP配置
- ✅ 依赖包
- ✅ 提供修复建议

### 2. 系统状态命令
```bash
carrymem status
# 或
python3 -m memory_classification_engine.cli_enhancements status
```
显示：
- 📊 数据库信息
- 📈 按类型统计
- 🔌 MCP连接状态
- 🎯 最近活动

### 3. MCP自动配置
```bash
carrymem setup-mcp --tool claude
# 或
python3 -m memory_classification_engine.cli_enhancements setup-mcp
```
支持：
- Claude Desktop
- Cursor

详见：[CLI增强功能指南](CLI_ENHANCEMENTS_GUIDE.md)

---

## 📖 按场景查找文档

### 场景1：我是新用户，想快速上手
1. 运行 `bash install.sh` 一键安装
2. 阅读 [快速开始指南](QUICK_START_GUIDE.md)
3. 遇到问题查看 [快速修复指南](QUICK_FIX_GUIDE.md)

### 场景2：安装遇到问题
1. 运行 `carrymem doctor` 诊断
2. 查看 [故障排除](TROUBLESHOOTING.md)
3. 查看 [快速修复指南](QUICK_FIX_GUIDE.md)

### 场景3：想配置MCP集成
1. 运行 `carrymem setup-mcp --tool claude`
2. 阅读 [CLI增强功能指南](CLI_ENHANCEMENTS_GUIDE.md)

### 场景4：想了解系统状态
1. 运行 `carrymem status`
2. 运行 `carrymem stats`

### 场景5：我是开发者，想贡献代码
1. 阅读 [架构文档](ARCHITECTURE.md)
2. 阅读 [API参考](API_REFERENCE.md)
3. 查看 [路线图](ROADMAP.md)
4. 查看 [优化建议](OPTIMIZATION_RECOMMENDATIONS.md)

---

## 🔧 命令速查表

### 基础命令
```bash
carrymem init                    # 初始化数据库
carrymem add "message"           # 添加记忆
carrymem list                    # 列出记忆
carrymem search "query"          # 搜索记忆
carrymem stats                   # 统计信息
```

### 诊断命令（新）
```bash
carrymem doctor                  # 系统诊断
carrymem status                  # 系统状态
carrymem setup-mcp --tool claude # MCP配置
```

### 管理命令
```bash
carrymem edit <key> "new text"   # 编辑记忆
carrymem forget <key>            # 删除记忆
carrymem clean                   # 清理过期记忆
carrymem export <path>           # 导出记忆
carrymem import <path>           # 导入记忆
```

---

## 📁 文档目录结构

```
docs/
├── README.md                          # 本文档（文档索引）
├── QUICK_START_GUIDE.md               # 快速开始
├── QUICK_FIX_GUIDE.md                 # 快速修复 ⭐
├── TROUBLESHOOTING.md                 # 故障排除 ⭐
├── CLI_ENHANCEMENTS_GUIDE.md          # CLI增强功能 ⭐
├── USER_STORIES.md                    # 用户故事
├── ARCHITECTURE.md                    # 架构文档
├── API_REFERENCE.md                   # API参考
├── ROADMAP.md                         # 路线图
├── USER_READINESS_ASSESSMENT.md       # 可用性评估（内部）
├── OPTIMIZATION_RECOMMENDATIONS.md    # 优化建议（内部）
├── IMPLEMENTATION_SUMMARY.md          # 实施总结（内部）
├── PROJECT_REVIEW_2026-04-26.md       # 旧评审报告（归档）
├── guides/                            # 详细指南
├── development/                       # 开发文档
├── planning/                          # 规划文档
├── testing/                           # 测试文档
└── i18n/                              # 国际化文档
```

---

## ✅ 用户可用性检查清单

### 安装体验 ✅
- [x] 一键安装脚本 (install.sh)
- [x] 自动PATH配置
- [x] 依赖自动安装

### 故障排除 ✅
- [x] 快速修复指南
- [x] 详细故障排除文档
- [x] 自动诊断工具 (doctor命令)

### 文档完整性 ✅
- [x] 快速开始指南
- [x] 命令参考
- [x] 故障排除
- [x] API文档
- [x] 架构文档

### 系统可维护性 ✅
- [x] doctor命令（自动诊断）
- [x] status命令（状态监控）
- [x] setup-mcp命令（自动配置）

---

## 🆘 获取帮助

### 遇到问题？
1. **运行诊断**: `carrymem doctor`
2. **查看状态**: `carrymem status`
3. **查看文档**: 
   - [快速修复指南](QUICK_FIX_GUIDE.md)
   - [故障排除](TROUBLESHOOTING.md)

### 报告问题
- GitHub Issues: [提交问题](https://github.com/yourusername/carrymem/issues)
- 邮件: support@carrymem.dev

---

## 📝 更新日志

### v0.2.0 (2026-04-27)
- ✅ 新增 doctor 命令（系统诊断）
- ✅ 新增 status 命令（系统状态）
- ✅ 改进 setup-mcp 命令（自动配置）
- ✅ 新增一键安装脚本
- ✅ 完善故障排除文档
- ✅ 新增CLI增强功能指南

### v0.1.0 (2026-04-26)
- 初始版本

---

**提示**: 标记 ⭐ 的文档是新用户必读文档！

**最后更新**: 2026-04-27  
**维护者**: CarryMem Team
