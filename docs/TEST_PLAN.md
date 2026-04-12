# Memory Classification Engine 测试计划 v2.0

> **版本**: 2.0  
> **更新日期**: 2026-04-13  
> **作者**: 产品经理 + 测试经理 联合审核  
> **状态**: 已批准执行

---

## 📌 经验教训总结（v1.0 → v2.0 关键改进）

### ❌ v1.0 的问题（已修复）

| # | 问题 | 影响 | 教训 |
|---|------|------|------|
| 1 | **测试哲学错误**：放宽断言让测试通过 | 掩盖了真实 bug（日期正则误匹配数字） | **测试必须严格！发现问题是第一目标** |
| 2 | **国际化测试缺失**：只测英文 | 日文规则完全缺失未被发现 | **产品面向 EN/ZH/JP，测试必须三语覆盖** |
| 3 | **规则完整性未验证** | advanced_rules.json 日文=0条规则 | **配置文件也必须纳入测试范围** |
| 4 | **段错误未捕获** | tier3.py JSON 解析崩溃 | **必须测试异常输入和边界情况** |
| 5 | **README 语言不一致** | 英文版混入中文示例 | **文档也是产品的一部分** |

---

## 一、当前测试覆盖情况（2026-04-13 更新）

### 1. 测试统计

| 类别 | 文件 | 用例数 | 通过率 | 状态 |
|------|------|:-------:|:------:|:----:|
| 核心功能 | test_core_functionality.py | 8 | 100% | ✅ |
| 高级分类 | test_advanced_classification.py | ~15 | 100% | ✅ |
| 社区反馈 | test_community_feedback.py | 5 | 100% | ✅ |
| MCP服务器 | test_mcp_server.py | 12 | 100% | ✅ |
| API客户端 | **test_api_client.py** | **21** | **100%** | ✅ 新增 |
| 多语言 | **test_multilingual.py** | **30** | **96.7%** | ✅ 新增 |
| 存储集成 | test_storage_integration.py | ~20 | ~70% | ⚠️ 字段映射问题 |
| 其他 | (10个文件) | ~55 | 100% | ✅ |
| **总计** | **17个文件** | **~166** | **~97%** | 🔄 |

### 2. 已覆盖的组件

```
✅ src/memory_classification_engine/engine.py          - 核心引擎
✅ src/memory_classification_engine/api/client.py      - API客户端
✅ src/memory_classification_engine/storage/tier2.py    - 程序记忆存储
✅ src/memory_classification_engine/storage/tier3.py    - 情景记忆存储
✅ src/memory_classification_engine/layers/             - 分类层
✅ config/advanced_rules.json                          - 规则配置
✅ mce-mcp/server.py                                   - MCP服务器
```

### 3. 未覆盖或覆盖不足的组件

| 组件 | 路径 | 当前覆盖 | 优先级 |
|------|------|:--------:|:------:|
| 插件系统 | `src/plugins/` | 0% | 🔴 P0 |
| 隐私模块 | `src/privacy/` | 0% | 🔴 P0 |
| SDK模块 | `src/sdk/` | 0% | 🔴 P0 |
| 分类管道集成 | `coordinators/classification_pipeline.py` | 30% | 🟡 P1 |
| 存储协调器 | `coordinators/storage_coordinator.py` | 40% | 🟡 P1 |
| 知识图谱 | `src/knowledge/` | 0% | 🟢 P2 |
| Web界面 | `src/web/` | 0% | 🟢 P2 |

---

## 二、测试策略（基于经验教训重新定义）

### 🎯 核心原则

```
┌─────────────────────────────────────────────────────────────┐
│                    测试核心原则                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1️⃣  STRICT ASSERTIONS ONLY                                │
│     → 绝不放宽断言让测试通过                                  │
│     → 测试失败 = 发现了需要修复的问题                         │
│                                                             │
│  2️⃣  INTERNATIONALIZATION FIRST                             │
│     → 产品面向 EN/ZH/JP                                     │
│     → 每个功能点必须有三种语言的测试用例                       │
│                                                             │
│  3️⃣  CONFIGURATION AS CODE                                 │
│     → rules.yaml / advanced_rules.json 也是代码              │
│     → 必须验证规则的完整性和准确性                            │
│                                                             │
│  4️⃣  BOUNDARY & EDGE CASES                                 │
│     → 正常路径 ≠ 全部场景                                    │
│     → 必须测试异常输入、空值、超长字符串、特殊字符              │
│                                                             │
│  5️⃣  TEST-DRIVEN BUG FIXING                                │
│     → 测试暴露的问题 → 立即修复 → 回归测试                    │
│     → 不记录 = 没发生                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 测试金字塔（MCE 特化）

```
        ┌───────────────────┐
        │   E2E Tests       │  ← 用户旅程、跨语言工作流
        │   (少量, 关键路径)  │
        ├───────────────────┤
        │ Integration Tests │  ← 三层分类管道、存储集成、多语言
        │   (中等数量)       │
        ├───────────────────┤
        │  Unit Tests       │  ← 每个分类器、每条规则、每种语言
        │   (大量, 快速)     │
        ├───────────────────┤
        │  Static Analysis  │  ← 规则完整性检查、配置验证
        │   (自动化)         │
        └───────────────────┘
```

---

## 三、详细测试计划

### Phase 1: 基础巩固（P0 - 本周完成）✅ 大部分已完成

#### 1.1 多语言规则完整性测试 ✅ 已完成

**目标**: 确保每种语言有完整的规则覆盖

**测试用例模板**:

```python
# 对每种语言，验证以下7种记忆类型都有对应规则：
TEST_MATRIX = {
    "user_preference": {"en": ["I prefer", "I like"], "zh": ["我喜欢", "偏好"], "ja": ["好む", "好き"]},
    "correction": {"en": ["too complex", "wrong"], "zh": ["太复杂", "不对"], "ja": ["複雑すぎる"]},
    "decision": {"en": ["let's use", "decided to"], "zh": ["决定用", "选择"], "ja": ["決定する"]},
    "relationship": {"en": ["handles", "responsible for"], "zh": ["负责", "主管"], "ja": ["担当"]},
    "task_pattern": {"en": ["always run", "need to"], "zh": ["每次都要", "需要"], "ja": ["必ず実行"]},
    "sentiment_marker": {"en": ["frustrating", "annoying"], "zh": ["太繁琐", "烦人"], "ja": ["面倒くさい"]},
    "fact_declaration": {"en": ["we have X employees"], "zh": ["我们有X人"], "ja": ["X名の従業員"]},
}
```

**已发现问题并修复**:
- ✅ `advanced_rules.json` 日文规则从 0 条 → 7 条
- ✅ 日期正则过于宽泛 → 严格化为 YYYY-MM-DD 格式
- ✅ 中文 relationship 规则缺失 → 新增"负责/主管+后端/前端"

#### 1.2 API 客户端测试 ✅ 已完成

**文件**: [test_api_client.py](../tests/test_api_client.py)  
**用例数**: 21  
**覆盖率**: 100%

#### 1.3 段错误/崩溃防护测试 ✅ 已完成

**已修复**:
- [tier3.py](../src/memory_classification_engine/storage/tier3.py#L1049-L1090): JSON 解析增加 try-catch
- 新增回归测试: 空内容、损坏数据、超长字符串

---

### Phase 2: 核心扩展（P0/P1 - 下周完成）

#### 2.1 插件系统测试 🔴 待开发

```python
# tests/test_plugin_manager.py

class TestPluginManager:
    """插件管理器测试"""
    
    def test_load_builtin_plugins(self):
        """加载内置插件"""
        
    def test_plugin_lifecycle(self):
        """插件生命周期: 注册→启用→禁用→卸载"""
        
    def test_plugin_isolation(self):
        """插件间隔离性: 一个插件崩溃不影响其他"""
        
    def test_plugin_configuration(self):
        """插件配置热重载"""
        

class TestBuiltinPlugins:
    """内置插件功能测试"""
    
    def test_nudge_plugin(self):
        """提醒机制插件"""
        
    def test_quality_plugin(self):
        """记忆质量评估插件"""
        
    def test_community_plugin(self):
        """社区反馈插件"""
```

#### 2.2 隐私模块测试 🔴 待开发

```python
# tests/test_privacy_module.py

class TestAccessControl:
    """访问控制测试"""
    
    def test_user_can_access_own_memories(self):
        """用户只能访问自己的记忆"""
        
    def test_tenant_isolation(self):
        """租户间数据隔离"""
        
    def test_admin_privileges(self):
        """管理员权限边界"""
        

class TestEncryption:
    """加密功能测试"""
    
    def test_encryption_decryption_roundtrip(self):
        """加密解密往返一致性"""
        
    def test_different_key_ids(self):
        """不同密钥ID的隔离"""
        
    def test_corrupted_ciphertext_handling(self):
        """损坏密文处理（不崩溃）"""
        

class TestAuditLog:
    """审计日志测试"""
    
    def test_sensitive_operations_logged(self):
        """敏感操作被记录"""
        
    def test_log_tamper_detection(self):
        """日志篡改检测"""
```

#### 2.3 SDK 模块测试 🔴 待开发

```python
# tests/test_sdk_module.py

class TestSDKClient:
    """SDK客户端测试"""
    
    def test_quick_start_example(self):
        """快速开始示例可运行"""
        
    def test_async_operations(self):
        """异步操作正确性"""
        
    def test_error_handling(self):
        """错误处理和重试机制"""
        

class TestSDKExceptions:
    """SDK异常测试"""
    
    def test_network_timeout(self):
        """网络超时异常"""
        
    def test_authentication_failure(self):
        """认证失败异常"""
        
    def test_rate_limiting(self):
        """速率限制异常"""
```

---

### Phase 3: 深度验证（P1/P2 - 2-4周）

#### 3.1 分类管道集成测试

```python
# tests/test_classification_pipeline_integration.py

class TestThreeLayerPipeline:
    """三层分类管道集成测试"""
    
    def test_layer1_rule_match_priority(self):
        """Layer1 规则匹配优先于 Layer2/3"""
        
    def test_layer2_pattern_analysis_fallback(self):
        """Layer2 在 Layer1 未匹配时触发"""
        
    def test_layer3_semantic_last_resort(self):
        """Layer3 作为最后手段"""
        
    def test_confidence_score_degradation(self):
        """置信度随层级递减"""
        

class TestCrossLanguagePipeline:
    """跨语言分类管道测试"""
    
    def test_mixed_language_input(self):
        """混合语言输入处理"""
        
    def test_language_switch_mid_conversation(self):
        """会话中途语言切换"""
        
    def test_code_with_multilingual_comments(self):
        """多语言注释的代码块"""
```

#### 3.2 性能基准测试

```python
# tests/test_performance_benchmark.py

class TestClassificationPerformance:
    """分类性能基准"""
    
    def test_single_message_latency_p50(self):
        """单消息延迟 P50 < 100ms"""
        
    def test_batch_processing_throughput(self):
        """批处理吞吐量 > 100 msg/s"""
        
    def test_memory_usage_stability(self):
        """长时间运行内存不泄漏"""
        

class TestStoragePerformance:
    """存储性能基准"""
    
    def test_retrieval_latency_by_tier(self):
        """各层检索延迟: Tier2 < Tier4 < Tier3"""
        
    def test_large_dataset_query(self):
        """大数据集查询性能 (>10k memories)"""
```

#### 3.3 并发与稳定性测试

```python
# tests/test_concurrent_stability.py

class TestConcurrentAccess:
    """并发访问测试"""
    
    def test_100_simultaneous_classifications(self):
        """100个同时分类请求"""
        
    def test_read_write_conflict(self):
        """读写冲突处理"""
        
    def test_connection_pool_exhaustion(self):
        """连接池耗尽时的优雅降级"""
```

---

### Phase 4: 产品质量保障（持续进行）

#### 4.1 回归测试套件

**每次发布前必须通过的检查清单**:

```
□ 所有单元测试通过 (166+ 用例)
□ 多语言严格测试通过 (30 用例)
□ 规则完整性检查通过
□ 性能基准无退化 (>5%)
□ 无新增段错误/崩溃
□ README 示例可运行
□ Git 提交信息规范
```

#### 4.2 配置文件静态分析

```python
# tests/test_config_validation.py

class TestRulesCompleteness:
    """规则完整性静态检查"""
    
    def test_each_language_has_all_memory_types(self):
        """每种语言必须覆盖全部7种记忆类型"""
        
    def test_no_overly_broad_regex(self):
        """正则不会误匹配无关内容"""
        
    def test_rule_priority_consistent(self):
        """规则优先级合理"""
        

class TestDocumentationConsistency:
    """文档一致性检查"""
    
    def test_readme_examples_match_locale(self):
        """英文 README 不包含中文示例"""
        
    def test_api_docs_match_implementation(self):
        """API 文档与实现一致"""
```

---

## 四、测试执行流程

### 日常开发流程

```
开发者提交代码
      ↓
自动触发 CI
      ↓
┌─────────────────────────────────────┐
│  1. 单元测试 (pytest)               │  ← 必须 100% 通过
│  2. 多语言测试 (EN/ZH/JP)           │  ← 必须 100% 通过
│  3. 规则完整性检查                   │  ← 必须通过
│  4. 代码覆盖率报告                  │  ← 目标 ≥85%
│  5. 性能基准对比                    │  ← 退化 >5% 则警告
└─────────────────────────────────────┘
      ↓
  全部通过 → 合并 PR
  有失败   → 开发者修复
```

### 发布前检查清单

```
Phase 1 完成:
  □ 插件系统测试通过
  □ 隐私模块测试通过  
  □ SDK 模块测试通过

Phase 2 完成:
  □ 分类管道集成测试通过
  □ 性能基准测试通过
  □ 并发稳定性测试通过

质量门禁:
  □ 无 P0/P1 缺陷
  □ 文档已更新
  □ CHANGELOG 已填写
  □ 回归测试套件全绿
```

---

## 五、关键指标（KPIs）

| 指标 | 当前值 | 目标值 | 测量方法 |
|------|:------:|:------:|----------|
| **单元测试用例数** | 166+ | 200+ | pytest --collect-only |
| **多语言测试覆盖** | 30/30 | 50/50 | test_multilingual.py |
| **代码覆盖率** | ~70% | ≥85% | pytest-cov |
| **规则完整性** | 28/28 | 28/28+ | test_config_validation.py |
| **CI 通过率** | ~97% | 100% | GitHub Actions |
| **平均测试耗时** | ~15s | <30s | pytest timing |
| **P0 缺陷修复时间** | N/A | <24h | Issue tracking |

---

## 六、风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|:------:|:----:|----------|
| 规则膨胀导致维护困难 | 中 | 高 | 自动化规则生成工具 |
| 多语言同步成本高 | 中 | 中 | 共享测试矩阵模板 |
| 第三方依赖变更导致测试失败 | 低 | 高 | Mock 外部服务 |
| 性能测试环境不稳定 | 中 | 中 | 使用专用基准环境 |

---

## 七、经验教训记录（持续更新）

### 2026-04-13: 国际化测试重大遗漏

**事件**: 
- 发现 `advanced_rules.json` 日文规则为 0 条
- 日期正则 `(\\d{1,4}[-/\\.\\s]?){2,3}` 过于宽泛，将 "100 employees" 错误分类为 event

**根因**:
- 测试只关注"能跑通"，未验证规则完整性
- 为通过测试而放宽断言，掩盖了真实 bug

**改进措施**:
1. ✅ 新增 `test_config_validation.py` 静态检查规则完整性
2. ✅ 恢复严格断言，测试失败 = 发现问题
3. ✅ 每种语言必须有同等深度的规则覆盖
4. ✅ 将此教训写入团队知识库

---

## 八、下一步行动

### 本周（Week 1）
- [x] ~~多语言测试~~ ✅ 
- [x] ~~API 客户端测试~~ ✅
- [x] ~~规则完整性修复~~ ✅
- [ ] **插件系统测试** ← 当前重点
- [ ] **隐私模块测试**

### 下周（Week 2）
- [ ] SDK 模块测试
- [ ] 分类管道集成测试
- [ ] 配置文件静态分析测试

### 第 3-4 周
- [ ] 性能基准测试
- [ ] 并发稳定性测试
- [ ] CI/CD 流水线完善

---

## 附录

### A. 测试文件命名规范

```
test_{module}_{feature}.py

示例:
- test_engine_core.py           # 引擎核心功能
- test_engine_multilingual.py   # 引擎多语言支持
- test_api_client.py            # API 客户端
- test_storage_tier3.py         # Tier3 存储
- test_rules_completeness.py    # 规则完整性
- test_config_validation.py     # 配置验证
```

### B. 测试用例编写规范

```python
def test_{scenario}_{expected_behavior}(self):
    """
    测试 {scenario} 场景下的 {expected_behavior} 行为。
    
    Given: 前置条件
    When:  执行动作
    Then:  预期结果
    
    严格断言: 使用 assert，绝不 return
    多语言: 如适用，提供 EN/ZH/JP 三个版本
    边界: 包含正常、边界、异常三种情况
    """
    # Arrange
    # Act
    # Assert (STRICT!)
```

### C. 参考链接

- [当前测试结果](../tests/) - 运行 `pytest tests/ -v` 查看
- [规则配置文件](../config/advanced_rules.json) - 28 条 EN/ZH/JP 规则
- [多语言测试套件](../tests/test_multilingual.py) - 30 个严格断言用例
- [Git 提交历史](https://github.com/lulin70/memory-classification-engine) - 变更追踪

---

**文档维护者**: 产品经理 + 测试经理  
**下次评审日期**: 2026-04-20  
**版本历史**: v1.0 (初始) → v2.0 (国际化强化)
