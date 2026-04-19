# MCE Documentation Index

## 📚 Documentation Structure

```
docs/
├── README.md                    # 本索引文件
├── api/                         # API Reference
│   ├── API_REFERENCE_V1.md
│   ├── api.md
│   ├── memory_format.md
│   └── sdk.md
├── architecture/                # Architecture & Design
│   ├── architecture.md          # Core architecture (EN)
│   ├── architecture-zh.md       # Core architecture (ZH)
│   ├── design.md                # System design
│   ├── design-zh.md             # System design (ZH)
│   ├── design-jp.md             # System design (JP)
│   └── mce_cross_session_memory_design.md
├── blog/                        # Blog posts & articles
│   └── why-your-agent-needs-professional-memory-classification.md
├── consensus/                   # Strategic decisions & consensus
│   ├── MCP_POSITIONING_CONSENSUS_v3.md    # ⭐ Current: Route B decision
│   ├── COMPETITOR_ANALYSIS_CONSENSUS_v2.md
│   ├── STRATEGIC_REVIEW_CONSENSUS_20260419.md
│   └── MCE_V2_CONSENSUS_FUSION.md
├── demo_report/                 # Demo interaction reports
│   └── DEMO_INTERACTION_REPORT_v1.md
├── planning/                    # Roadmaps & plans (v0.2.x legacy)
│   ├── DEVELOPMENT_MODIFICATION_PLAN_V2.md
│   ├── FEATURE_IMPLEMENTATION_STATUS.md
│   ├── OPTIMIZATION_ROADMAP_V1.md
│   └── RELEASE_PREP_PLAN_V1.md
├── privacy_enhancement/         # Privacy & security design
│   ├── requirements.md
│   ├── design.md
│   ├── implementation_plan.md
│   └── test_plan.md
├── product-manager/             # PM artifacts
│   └── USER_STORY_CALIBRATION_v1.md
├── review/                      # Code review reports
│   ├── D2-5_FULL_TEAM_REVIEW_REPORT.md
│   └── INSTALLATION_GUIDE_LINE_BY_LINE_AUDIT.md
├── testing/                     # Test plans & reports
│   ├── MCE_TEST_PLAN.md
│   ├── MCE_TEST_PLAN_V2.md
│   ├── MCE_TEST_REPORT.md      # through V3
│   ├── MCP_SERVER_TEST_PLAN.md
│   └── MCP_SERVER_TEST_REPORT_FINAL.md
├── user_guides/                 # User guides & tutorials
│   ├── installation_guide.md    # Legacy v0.1
│   ├── installation_guide_v2.md # Current v0.2+
│   ├── STORAGE_STRATEGY.md     # ⭐ Downstream integration guide
│   ├── user_guide.md           # EN
│   ├── user_guide-zh.md        # ZH
│   ├── user_guide-jp.md        # JP
│   ├── testing.md              # Testing guide
│   └── user_stories.md         # User stories collection
└── config/                      # Configuration examples
    ├── claude_code_mcp_config.md
    ├── workbuddy_mcp_config.md
    └── trae_sdk_integration.md
```

## 🎯 Key Documents (Priority Reading)

### For New Contributors
1. [README.md](../README.md) — Project overview & quick start
2. [CONTRIBUTING.md](../CONTRIBUTING.md) — Contribution guidelines
3. [architecture/architecture.md](./architecture/architecture.md) — System architecture

### For Strategic Decisions
1. **[MCP_POSITIONING_CONSENSUS_v3.md](./consensus/MCP_POSITIONING_CONSENSUS_v3.md)** ⭐
   - Route B decision: Pure upstream classification middleware
   - Tool reduction: 11 → 4
   - MemoryEntry Schema v1.0 specification

2. [COMPETITOR_ANALYSIS_CONSENSUS_v2.md](./consensus/COMPETITOR_ANALYSIS_CONSENSUS_v2.md)
   - 7 competitor deep-dive analysis
   - Gap identification

### For Development
1. [ROADMAP.md](../ROADMAP.md) — Current execution roadmap (v3.0.0)
2. [MCE-Bench Results](../benchmarks/classification_accuracy.py) — 180-case accuracy benchmark
3. [STORAGE_STRATEGY.md](./user_guides/STORAGE_STRATEGY.md) — Adapter integration guide

## 📖 Document Status Legend

| Status | Meaning |
|--------|---------|
| ✅ Active | Current version in use |
| 📝 Draft | Under development |
| 🔒 Frozen | Historical reference, not updated |
| 🗑️ Deprecated | Superseded by newer version |

## 🌐 i18n Documents

| Language | README | Roadmap | Architecture | User Guide |
|----------|--------|---------|--------------|------------|
| English (EN) | [README.md](../README.md) | [ROADMAP.md](../ROADMAP.md) | [architecture.md](./architecture/architecture.md) | [user_guide.md](./user_guides/user_guide.md) |
| Chinese (CN) | [README-CN.md](../README-CN.md) | [ROADMAP-CN.md](../ROADMAP-CN.md) | [architecture-zh.md](./architecture/architecture-zh.md) | [user_guide-zh.md](./user_guides/user_guide-zh.md) |
| Japanese (JP) | [README-JP.md](../README-JP.md) | [ROADMAP-JP.md](../ROADMAP-JP.md) | [design-jp.md](./architecture/design-jp.md) | [user_guide-jp.md](./user_guides/user_guide-jp.md) |

---

**Last Updated**: 2026-04-19 (Phase A+B completion)
**Maintainer**: MCE Core Team
