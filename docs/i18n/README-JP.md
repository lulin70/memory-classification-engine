# CarryMem

**AI があなたを覚える。その逆ではない。**

> ポータブル AI メモリレイヤー — モデル、ツール、デバイスを越えて

CarryMem は、AI アシスタントがあなたの好み、訂正、決定を記憶できるポータブル AI メモリシステムです。ツールを変えても記憶は失われず、デバイスを変えても持ち運べます。

[English](../../README.md) | [中文](README-CN.md) | **日本語**

<p align="center">
  <img src="https://img.shields.io/badge/version-0.4.3-blue" alt="Version">
  <img src="https://img.shields.io/badge/tests-224%20passing-green" alt="Tests">
  <img src="https://img.shields.io/badge/accuracy-90.6%25-green" alt="Accuracy">
  <img src="https://img.shields.io/badge/zero--cost-60%25%2B-brightgreen" alt="Zero Cost">
</p>

---

## 🎯 なぜ CarryMem が必要か？

### 問題：AI はいつもあなたを忘れる

新しい会話のたびに、AI は初めて会ったかのように振る舞います：
- ❌ あなたの好み？忘れている
- ❌ あなたの訂正？忘れている
- ❌ あなたの決定？忘れている

ツールを変え（Cursor → Windsurf）、モデルを変え（Claude → GPT）、毎回ゼロからやり直し。

### 解決策：CarryMem

✅ **AI が自動的にあなたを記憶** — 好み、訂正、決定を自動分類して保存
✅ **メモリはポータブル** — エクスポート/インポート、ツールを変えてもデータは失われない
✅ **60%+ ゼロコスト** — スマート分類、トークンの無駄遣いなし
✅ **5分でセットアップ** — 設定不要、すぐに使える

---

## ⚡ クイックスタート

### インストール

```bash
pip install carrymem
```

### 最初のメモリ（1分）

```python
from memory_classification_engine import CarryMem

with CarryMem() as cm:
    # AI が自動的にあなたの好みを分類して保存
    cm.classify_and_remember("I prefer dark mode")
    cm.classify_and_remember("I use PostgreSQL for databases")
    cm.classify_and_remember("I work at a startup in Tokyo")

    # メモリの呼び出し
    memories = cm.recall_memories(query="database")
    for mem in memories:
        print(f"{mem['type']}: {mem['content']}")
```

これだけ！🎉 CarryMem は `~/.carrymem/memories.db` に自動的にデータベースを作成します。

---

## 💡 コア機能

### 1. 自動分類（7つのメモリタイプ）

CarryMem はメッセージタイプを自動識別し、価値のある情報だけを保存します：

```python
cm.classify_and_remember("I prefer dark mode")
# → type: user_preference, confidence: 0.95

cm.classify_and_remember("No, I meant Python 3.11, not 3.10")
# → type: correction, confidence: 0.98

cm.classify_and_remember("Let's use React for the frontend")
# → type: decision, confidence: 0.92
```

**7つのメモリタイプ**：`user_preference` · `correction` · `fact_declaration` · `decision` · `relationship` · `task_pattern` · `sentiment_marker`

### 2. セマンティックリコール（v0.4.0+）

```python
# 中国語で保存、英語で検索 — 言語を越えたリコール！
cm.classify_and_remember("我偏好使用PostgreSQL")

# 以下の検索でこのメモリが見つかります：
memories = cm.recall_memories(query="PostgreSQL")      # ✅ 完全一致
memories = cm.recall_memories(query="数据库")            # ✅ 同義語展開
memories = cm.recall_memories(query="Postgres")          # ✅ スペル修正
memories = cm.recall_memories(query="データベース")      # ✅ 言語間マッピング（日本語）
```

**機能**：同義語展開 · スペル修正 · 言語間マッピング（中/英/日） · 外部依存なし

### 3. アクティブ宣言

```python
cm.declare("I prefer PostgreSQL over MySQL")
# → confidence=1.0、確実に記憶される
```

### 4. メモリプロファイル

```python
profile = cm.get_memory_profile()
print(profile['summary'])
# → "AI はあなたについて12のことを記憶：5つの好み、3つの訂正、2つの決定"
```

### 5. エクスポート＆インポート（ポータビリティ）

```python
# メモリをエクスポート — データはあなたのもの
cm.export_memories(output_path="my_memories.json")

# 新しいデバイスでインポート
with CarryMem() as cm2:
    cm2.import_memories(input_path="my_memories.json")
    # すべてのメモリが復元！
```

---

## 🎨 実際の使用例

### 使用例 1：コードアシスタントがあなたのスタイルを記憶

```python
with CarryMem() as cm:
    cm.classify_and_remember("I prefer using type hints in Python")
    cm.classify_and_remember("I like to use dataclasses instead of dicts")

    # 次の会話で、AI はあなたの好みを自動的に知っている
    memories = cm.recall_memories(query="Python coding style")
```

### 使用例 2：ツール間での利用

```python
# Cursor で
with CarryMem(namespace="cursor") as cm_cursor:
    cm_cursor.classify_and_remember("I prefer dark mode")

# Windsurf で、同じメモリを使用
with CarryMem(namespace="cursor") as cm_windsurf:
    memories = cm_windsurf.recall_memories(query="theme")  # 見つかった！
```

### 使用例 3：プロジェクト分離

```python
# プロジェクト A
with CarryMem(namespace="project-a") as cm_a:
    cm_a.classify_and_remember("Use React for frontend")

# プロジェクト B — 干渉なし
with CarryMem(namespace="project-b") as cm_b:
    cm_b.classify_and_remember("Use Vue for frontend")
```

---

## 🔥 なぜ CarryMem が優れているか

|  | CarryMem | Mem0 | LangMem | Zep |
|--|----------|------|---------|-----|
| **自動分類** | ✅ 7タイプ | ❌ 全保存 | ⚠️ LLMが必要 | ⚠️ 事後要約 |
| **ポータビリティ** | ✅ あなたのファイル | ❌ クラウドロックイン | ❌ ツールロックイン | ❌ サービスロックイン |
| **コスト** | ✅ 60%+ ゼロコスト | ❌ 毎回呼び出し | ❌ 毎回呼び出し | ❌ 毎回呼び出し |
| **プロジェクト分離** | ✅ ネームスペース | ❌ なし | ❌ なし | ❌ なし |
| **ナレッジベース** | ✅ Obsidian | ❌ なし | ❌ なし | ❌ なし |
| **オープンソース** | ✅ 完全公開 | ⚠️ 一部 | ✅ 完全公開 | ⚠️ 一部 |

**主な違い**：CarryMem のメモリはあなたのもの。モデル、ツール、デバイスを変えても — メモリはついてくる。

---

## 📊 パフォーマンス指標

| 指標 | 値 |
|------|-----|
| 分類精度 | **90.6%** |
| F1 スコア | **97.9%** |
| ゼロコスト分類 | **60%+** |
| リコールレイテンシ (P50) | **~45ms** |
| テスト通過 | **224/224** |

---

## 🏗️ 仕組み

### 3層分類戦略

```
ユーザー入力 → ルールエンジン (60%+) → パターン分析 (30%) → セマンティック (10%)
                  ↓                        ↓                        ↓
             ゼロコスト             ほぼゼロコスト            トークンコスト
             高速                   中速                     低速
```

**60%+ の分類は LLM 呼び出し不要！**

### データフロー

```
1. ユーザー入力
   ↓
2. 自動分類（7タイプ）
   ↓
3. スマート保存（重複排除 + TTL）
   ↓
4. セマンティックリコール（FTS5 + 同義語）
   ↓
5. 関連メモリを返却
```

---

## 🌟 高度な機能

### Obsidian ナレッジベース統合

```python
from memory_classification_engine import CarryMem, ObsidianAdapter

with CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault")) as cm:
    cm.index_knowledge()
    results = cm.recall_from_knowledge("Python design patterns")
```

### MCP サーバー

MCP クライアント設定（Claude Code、Cursor など）に追加：

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

**12ツール**：コア (3) · ストレージ (3) · ナレッジ (3) · プロファイル (2) · プロンプト (1)

---

## 📚 ドキュメント

- 📖 [クイックスタートガイド](../QUICK_START_GUIDE.md)
- 🏗️ [アーキテクチャ](../ARCHITECTURE.md)
- 📋 [API リファレンス](../API_REFERENCE.md)
- 🎯 [ユーザーストーリー](../USER_STORIES.md)
- 🗺️ [ロードマップ](../guides/ROADMAP.md)
- 🤝 [コントリビューション](../../CONTRIBUTING.md)

---

## 🎯 誰のためのものか？

**開発者** — ユーザーを記憶する必要がある AI エージェントを構築する人

**プロダクトチーム** — 分類ロジックをゼロから構築せずに永続メモリが必要な人

**パワーユーザー** — AI ツールに自分を記憶してほしい人

---

## 🚦 プロジェクトステータス

**現在のバージョン**：v0.4.3
**テスト**：224/224 通過
**精度**：90.6%

---

## 🤝 コントリビューション

コントリビューションを歓迎します！[コントリビューションガイド](../../CONTRIBUTING.md)を参照してください。

### 開発環境のセットアップ

```bash
git clone https://github.com/lulin70/memory-classification-engine.git
cd carrymem
pip install -e ".[dev]"
pytest
```

---

## 📄 ライセンス

MIT ライセンス — 詳細は [LICENSE](../../LICENSE) を参照

---

**CarryMem を使い始めて、AI にあなたを記憶させよう！** 🚀

```bash
pip install carrymem
```
