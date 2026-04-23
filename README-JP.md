# CarryMem

**ポータブルAIメモリレイヤー。**

> すべてを覚えるのではない。重要なことだけを。

CarryMemはAIエージェントに永続的でポータブルなメモリレイヤーを提供します。会話をリアルタイムで分類し、記憶すべき内容を保存し、ユーザーがメモリをどこにでも持ち運べるようにします——モデルを超えて、ツールを超えて、デバイスを超えて。

**AIがあなたを覚える。その逆ではない。**

<p align="center">
  <img src="https://img.shields.io/badge/version-0.3.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/tests-133%20passing-green" alt="Tests">
  <img src="https://img.shields.io/badge/MCP-3%2B3%2B3%2B2%2B1-blue" alt="MCP">
  <img src="https://img.shields.io/badge/Accuracy-90.6%25-green" alt="Accuracy">
</p>

[English](README.md) | [中文](README-CN.md) | **日本語**

---

## 問題

AIエージェントと新しい会話を始めるたびに、あなたのことを忘れてしまいます。

あなたの好み、訂正、決定——すべて消えます。同じことを繰り返し言わなければなりません。エージェントは既に却下したものを推奨します。ClaudeからGPTに、CursorからWindsurfに、あるMCPサーバーから別のものに切り替えると、まるで初対面のようです。

既存のソリューションには3つの問題があります：

1. **メモリがロックインされている。** ほとんどのメモリツールはデータを独自のシステムに保存します。ツールを変えると、メモリを失います。
2. **すべてを保存する。** 会話全体をベクトルデータベースにダンプし、セマンティック検索で何とかしようとします。高価で、ノイズが多く、遅い。
3. **分類がない。** メッセージが*何であるか*（好み？訂正？雑談？）を理解しないと、検索は盲目です。

**60%以上のメッセージは保存すべきではありません。** しかし、現在のシステムはすべてを保存する（ノイズ爆発）か、何も保存しない（健忘）かのどちらかです。

CarryMemはこの3つすべてを解決します。

---

## 仕組み

```
ユーザーメッセージ → MCEエンジン（分類）→ ストレージ層（保存）→ エージェントコンテキスト（検索）
```

### ステップ1：分類（MCEエンジン）

すべてのユーザーメッセージは3層分類ファネルを通過します：

| 層 | 方法 | コスト | カバレッジ |
|---|------|--------|-----------|
| ルールマッチング | 正規表現 + キーワード | ゼロ | ~60% |
| パターン分析 | NLPパターン | ほぼゼロ | ~30% |
| セマンティック推論 | LLM（必要な場合のみ） | トークンコスト | <10% |

**60%以上の分類がゼロLLMコストで実行されます。**

### ステップ2：7つのメモリタイプに分類

| タイプ | 説明 | 例 |
|--------|------|-----|
| `user_preference` | 表明された好み | "ダークモードが好きです" |
| `correction` | AIへの明確な訂正 | "いや、Pythonバージョンのことです" |
| `fact_declaration` | ユーザーに関する事実 | "東京のスタートアップで働いています" |
| `decision` | 行った選択 | "Reactで行きましょう" |
| `relationship` | 社会的/コンテキスト情報 | "チームメイトがバックエンドを担当しています" |
| `task_pattern` | 繰り返しのワークフロー | "いつもREADMEから始めます" |
| `sentiment_marker` | 出力への感情的な反応 | "まさにこれが必要でした" |

### ステップ3：優先度ティアで保存

すべてのメモリが同等ではありません。CarryMemは分類された各メモリにティアを割り当てます：

| ティア | 名前 | デフォルトTTL | 説明 |
|--------|------|--------------|------|
| **Tier 1** | 感覚的 | 24時間 | 一時的な情報、急速な減衰 |
| **Tier 2** | 手続的 | 90日 | 習慣/好み、中期保持 |
| **Tier 3** | エピソード的 | 365日 | 重要なイベント、長期保持 |
| **Tier 4** | 意味的 | 永久 | コア知識、期限切れなし |

### ステップ4：必要な時に検索

新しい会話が始まると、CarryMemは関連するメモリをエージェントのコンテキストウィンドウに注入します。エージェントは単に応答するだけでなく、*覚えています*。

検索優先度：**メモリ > ナレッジベース > 外部LLM**

---

## クイックスタート

### インストール

```bash
pip install carrymem
```

### 分類 + 記憶（3行）

```python
from carrymem import CarryMem

cm = CarryMem()  # ~/.carrymem/memories.dbに自動SQLiteストレージ
result = cm.classify_and_remember("ダークモードが好きです")
# → {"type": "user_preference", "confidence": 0.95, "stored": True}
```

### 好みの宣言

```python
# ユーザーがAIに自分について積極的に伝える
result = cm.declare("ダークモードが好きです")
# → confidence=1.0, source_layer="declaration", 必ず保存
```

### AIが覚えていることを見る

```python
profile = cm.get_memory_profile()
# → {
#     "summary": "AIはあなたについて12の情報を記憶：5つの好み、3つの訂正、2つの決定",
#     "highlights": {"user_preference": ["ダークモード", "PostgreSQL"], ...},
#     "stats": {"by_type": {...}, "confidence_avg": 0.92}
#   }
```

### Obsidianナレッジベース

```python
from carrymem import CarryMem
from carrymem.adapters import ObsidianAdapter

cm = CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
cm.index_knowledge()
results = cm.recall_from_knowledge("Pythonデザインパターン")
```

### プロジェクトレベルの分離

```python
cm_alpha = CarryMem(namespace="project-alpha")
cm_beta = CarryMem(namespace="project-beta")

cm_alpha.declare("ダークモードが好きです")   # project-alphaに分離
cm_beta.declare("ライトモードが好きです")     # project-betaに分離

# クロスプロジェクト検索
result = cm_alpha.recall_all("PostgreSQL", namespaces=["project-alpha", "global"])
```

### スマートシステムプロンプト

```python
# エージェント用のコンテキスト認識システムプロンプトを生成
prompt = cm.build_system_prompt(context="ダークモード", language="ja")
# → 優先度順に関連メモリとナレッジベースを含む
```

### プラグインアダプター

```python
# entry_points経由でサードパーティアダプターをロード
from carrymem.adapters import load_adapter, list_available_adapters

CustomAdapter = load_adapter("my_custom_adapter")
adapters = list_available_adapters()
# → {"sqlite": "...", "obsidian": "...", "my_custom_adapter": "... (plugin)"}
```

### エクスポート＆インポート（ポータビリティ）

```python
# メモリをエクスポート——それはあなたのもの
result = cm.export_memories(output_path="my_memories.json")
# → {"exported": True, "total_memories": 42, "format": "json"}

# 人間が読めるMarkdownでエクスポート
result = cm.export_memories(output_path="my_memories.md", format="markdown")

# 新しいCarryMemインスタンスにインポート（別ツール、別デバイス）
cm2 = CarryMem(db_path="new_device.db")
cm2.import_memories(input_path="my_memories.json")
# → {"imported": 42, "skipped": 0, "errors": 0}
```

---

## MCPサーバー：3+3+3+2+1オプショナルモード

| グループ | ツール | 要件 |
|---------|-------|------|
| **コア (3)** | `classify_message`, `get_classification_schema`, `batch_classify` | 常に利用可能 |
| **ストレージ (3)** | `classify_and_remember`, `recall_memories`, `forget_memory` | ストレージアダプター |
| **ナレッジ (3)** | `index_knowledge`, `recall_from_knowledge`, `recall_all` | ナレッジアダプター |
| **プロファイル (2)** | `declare_preference`, `get_memory_profile` | ストレージアダプター |
| **プロンプト (1)** | `get_system_prompt` | ストレージアダプター |

### セットアップ

```json
{
  "mcpServers": {
    "carrymem": {
      "command": "python3",
      "args": ["-m", "memory_classification_engine.integration.layer2_mcp"],
      "env": {}
    }
  }
}
```

---

## 比較

|  | CarryMem | Mem0 | LangMem | Zep |
|--|----------|------|---------|-----|
| **分類** | リアルタイム、7タイプ | なし（フルダンプ） | LLMチェーン経由 | 事後サマリー |
| **ストレージ** | ポータブル（SQLite/あなたのDB） | Mem0クラウドにロックイン | LangChainにロックイン | Zepにロックイン |
| **LLMコスト** | 60%+ゼロコスト | 常時オンの埋め込み | 常時オンのLLM | 常時オンのLLM |
| **メモリタイプ** | 7つの構造化タイプ | 非構造化 | 3タイプ | 2タイプ |
| **忘却** | アクティブ（4ティアTTL） | TTLのみ | 手動 | TTLのみ |
| **ナレッジベース** | Obsidian（読み取り専用） | なし | なし | なし |
| **アクティブ宣言** | あり（confidence=1.0） | なし | なし | なし |
| **プロジェクト分離** | ネームスペースベース | なし | なし | なし |
| **オープンソース** | 完全 | 部分 | 完全 | 部分 |
| **ポータビリティ** | あなたのファイル、どこへでも | なし | なし | なし |

**重要な違い：** CarryMemのメモリはあなたのものです。私たちのものでも、他の誰のものでもありません。モデルを変えても、ツールを変えても、デバイスを変えても——あなたのメモリはついてきます。

---

## パフォーマンス

| メトリクス | 値 |
|-----------|-----|
| 分類精度 | **90.6%** |
| F1スコア | **97.9%** |
| 統合テスト | **133/133合格** |
| LLM呼び出し比率 | **<10%** |
| P50レイテンシ（ルールマッチ） | ~45ms |

---

## アーキテクチャ

```
CarryMem（メインクラス）
  ├── MCEエンジン（3層分類ファネル）
  │   ├── ルールマッチャー（60%+ヒット、ゼロコスト）
  │   ├── パターンアナライザー（30%+ヒット、ほぼゼロコスト）
  │   └── セマンティッククラシファイア（<10%ヒット、LLMフォールバック）
  ├── ストレージアダプター（SQLiteデフォルト、置き換え可能）
  │   ├── SQLiteAdapter: FTS5 + 重複排除 + TTL + ネームスペース
  │   ├── ObsidianAdapter: Markdown + Frontmatter + Wiki-links（読み取り専用）
  │   └── プラグインアダプター: entry_points経由
  ├── declare(): アクティブ宣言（confidence=1.0）
  ├── get_memory_profile(): 構造化メモリプロファイル
  ├── build_system_prompt(): スマートプロンプト生成（EN/CN/JP）
  ├── export_memories(): メモリエクスポート（JSON/Markdown）
  ├── import_memories(): メモリインポート（JSON）
  └── MCPサーバー: 3+3+3+2+1ツール
```

---

## プロジェクト構造

```
carrymem/
├── src/memory_classification_engine/
│   ├── carrymem.py              # CarryMemメインクラス
│   ├── engine.py                # MCEコアエンジン（スリム）
│   ├── adapters/
│   │   ├── base.py              # StorageAdapter ABC + MemoryEntry + StoredMemory
│   │   ├── sqlite_adapter.py    # SQLite + FTS5 + ネームスペース
│   │   ├── obsidian_adapter.py  # Obsidian（読み取り専用）
│   │   └── loader.py            # プラグインアダプターローダー
│   ├── layers/                  # 3層分類ファネル
│   ├── coordinators/            # 分類パイプライン
│   ├── utils/
│   │   ├── confirmation.py      # 確認パターン検出（EN/CN/JP）
│   │   └── ...
│   └── integration/layer2_mcp/  # MCPサーバー
├── tests/                       # 125テスト合格
├── benchmarks/                  # MCE-Bench 180ケースデータセット
├── docs/
│   ├── consensus/               # 戦略的決定
│   ├── architecture/            # アーキテクチャ + 設計ドキュメント
│   ├── planning/                # ユーザーストーリー + ステータス
│   └── testing/                 # テスト計画
└── setup.py                     # carrymem v0.3.0
```

---

## 対象者

**開発者** — セッションを越えてユーザーを覚える必要があるAIエージェントを構築する人。

**エージェント製品チーム** — 分類ロジックをゼロから構築せずに永続的メモリが必要な人。

**パワーユーザー** — AIツールに自分を覚えてほしい人。その逆ではない。

---

## ライセンス

MIT
