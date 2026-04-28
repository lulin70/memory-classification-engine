# CarryMem — AI のアイデンティティレイヤー

**AI はあなたが誰かを覚える。あなたが何を言ったかだけではない。**

> ポータブル AI アイデンティティレイヤー — 好み、決定、訂正がモデル、ツール、デバイスを越えてついてくる。

CarryMem は軽量・ゼロ依存の AI メモリシステムで、**あなたが誰か** — 好み、決定、訂正 — を保存し、そのアイデンティティをあらゆる AI ツールで利用可能にします。Cursor から Claude Code へ、GPT から Claude へ切り替えても、AI は常にあなたを知っています。

[English](../../README.md) | [中文](README-CN.md) | **日本語**

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.2-blue" alt="Version">
  <img src="https://img.shields.io/badge/tests-447%20passing-green" alt="Tests">
  <img src="https://img.shields.io/badge/accuracy-90.6%25-green" alt="Accuracy">
  <img src="https://img.shields.io/badge/zero--dependencies-core-brightgreen" alt="Zero Deps">
</p>

---

## なぜ CarryMem が必要か？

### 問題：AI はいつもあなたが誰かを忘れる

新しい会話のたびに、AI はゼロから始まります：
- ダークモードがお好み？**忘れている。**
- 前回訂正したこと？**忘れている。**
- React を使うと決めたこと？**忘れている。**

ツールを変え（Cursor → Windsurf）、モデルを変え（Claude → GPT）— 毎回ゼロからやり直し。

### 解決策：CarryMem アイデンティティレイヤー

CarryMem はテキストを保存するだけではなく — **あなたが誰か**を理解します：

```bash
$ carrymem whoami

  あなたは誰か（AI による）
  ==================================================

  あなたの好み：
    ⭐ すべてのエディタでダークモードが好き
    ⭐ データベースには PostgreSQL を使う
    ⭐ データ分析にはいつも Python を使う

  あなたの決定：
    🎯 フロントエンドは React を使う

  あなたの訂正：
    🔧 ポート番号は 5432 が正しい

  メモリプロファイル：
    合計: 19 | 主要タイプ: user_preference | 平均信頼度: 73%
```

---

## クイックスタート

### インストール

```bash
pip install -e .
```

### 5 行のコード

```python
from memory_classification_engine import CarryMem

cm = CarryMem()
cm.classify_and_remember("ダークモードが好き")              # 好みとして自動分類
cm.classify_and_remember("PostgreSQL を使って MySQL は使わない")  # 訂正として自動分類
memories = cm.recall_memories("データベース")                  # セマンティックリコール
print(cm.build_system_prompt())                               # 任意の AI に注入
cm.close()
```

### CLI（19 コマンド）

```bash
carrymem init                           # 初期化
carrymem add "ダークモードが好き"        # メモリを保存
carrymem add "テストメモ" --force        # 強制保存（分類をスキップ）
carrymem list                           # メモリ一覧
carrymem search "テーマ"                # メモリ検索
carrymem show <key>                     # メモリ詳細
carrymem edit <key> "新しい内容"         # メモリ編集
carrymem forget <key>                   # メモリ削除
carrymem whoami                         # AI が考えるあなた
carrymem profile export identity.json   # AI アイデンティティをエクスポート
carrymem stats                          # メモリ統計
carrymem check                          # 品質・競合チェック
carrymem clean --expired --dry-run      # クリーンアップのプレビュー
carrymem doctor                         # インストール診断
carrymem setup-mcp --tool cursor        # ワンライン MCP 設定
carrymem tui                            # ターミナル UI
carrymem export backup.json             # 全メモリをエクスポート
carrymem import backup.json             # メモリをインポート
carrymem version                        # バージョン表示
```

---

## コア機能

### 1. 自動分類（7つのメモリタイプ）

CarryMem は共有する情報の種類を自動的に識別します：

| タイプ | アイコン | 例 |
|--------|----------|-----|
| `user_preference` | ⭐ | "ダークモードが好き" |
| `correction` | 🔧 | "いや、Python 3.11 であって 3.10 ではない" |
| `decision` | 🎯 | "フロントエンドは React を使う" |
| `fact_declaration` | 📌 | "東京のスタートアップで働いている" |
| `task_pattern` | 🔄 | "いつもテストを先に書く" |
| `contextual_observation` | 👁 | "ユーザーはイライラしているようだ" |
| `knowledge` | 📚 | "PostgreSQL は MVCC を使用している" |

### 2. セマンティックリコール（言語間）

```python
cm.classify_and_remember("我偏好使用PostgreSQL")

# 以下の検索で見つかります：
cm.recall_memories("PostgreSQL")     # 完全一致
cm.recall_memories("数据库")          # 同義語展開
cm.recall_memories("Postgres")       # スペル修正
cm.recall_memories("データベース")    # 言語間マッピング（日本語）
```

### 3. アイデンティティレイヤー（whoami）

```python
identity = cm.whoami()
print(identity["preferences"])   # ["ダークモードが好き", ...]
print(identity["decisions"])     # ["フロントエンドは React", ...]
print(identity["corrections"])   # ["ポート番号は 5432", ...]
```

### 4. 重要度スコアリングとライフサイクル

すべてのメモリには時間とともに進化する重要度スコアがあります：

```
importance = confidence × type_weight × recency_factor × access_factor
```

- **30日半減期減衰** — 古いメモリはアクセスされなければ薄れる
- **アクセス強化** — 頻繁に呼び出されるメモリは新鮮に保たれる
- **タイプ重み付け** — 訂正 (1.3x) > 決定 (1.2x) > 好み (1.1x)

### 5. 品質管理

```bash
carrymem check                    # 全チェック
carrymem check --conflicts        # 矛盾を検出
carrymem check --quality          # 低品質メモリを発見
carrymem check --expired          # 期限切れメモリを発見
carrymem clean --expired --dry-run # クリーンアップのプレビュー
```

### 6. セキュリティと信頼性

| 機能 | 説明 |
|------|------|
| **暗号化** | AES-128 (Fernet) または HMAC-CTR フォールバック、ゼロ依存 |
| **バックアップ** | ゼロダウンタイム SQLite VACUUM INTO |
| **監査ログ** | 追記専用の操作履歴 |
| **バージョン履歴** | すべての編集を追跡、ロールバック対応 |
| **入力検証** | SQL インジェクション、XSS、パストラバーサル対策 |

### 7. MCP 統合（ワンライン設定）

```bash
# Cursor 用に設定
carrymem setup-mcp --tool cursor

# Claude Code 用に設定
carrymem setup-mcp --tool claude-code

# すべてに設定
carrymem setup-mcp --tool all
```

12 の MCP ツール：コア (3) · ストレージ (3) · ナレッジ (3) · プロファイル (2) · プロンプト (1)

### 8. ターミナル UI

```bash
pip install textual
carrymem tui
```

サイドバーフィルター、検索、追加モード付きのインタラクティブターミナルインターフェース。

---

## 競合比較

|  | CarryMem | Mem0 | OpenChronicle | ima |
|--|----------|------|---------------|-----|
| **ゼロ依存** | ✅ SQLite のみ | ❌ Milvus 必要 | ✅ | ❌ クラウド |
| **自動分類** | ✅ 7 タイプ | ❌ | ❌ 手動 | ❌ |
| **アイデンティティポートレート** | ✅ whoami | ❌ | ❌ | ❌ |
| **CLI** | ✅ 19 コマンド | ❌ | ❌ | ❌ |
| **TUI** | ✅ textual | ❌ | ❌ | ✅ アプリ |
| **暗号化** | ✅ 内蔵 | ❌ | ❌ | ❌ |
| **バージョン履歴** | ✅ ロールバック | ❌ | ❌ | ❌ |
| **競合検出** | ✅ 内蔵 | ❌ | ❌ | ❌ |
| **データ所有権** | ✅ ローカルファイル | ⚠️ クラウド | ✅ ローカル | ❌ クラウド |
| **5 行統合** | ✅ | ❌ | ❌ | ❌ |
| **言語間リコール** | ✅ 中/英/日 | ❌ | ❌ | ❌ |

**主な違い**：他の製品はあなたが何を読んだかを保存する。CarryMem はあなたが誰かを保存する。

---

## パフォーマンス

| 指標 | 値 |
|------|-----|
| 分類精度 | **90.6%** |
| F1 スコア | **97.9%** |
| ゼロコスト分類 | **60%+** |
| リコールレイテンシ (P50) | **~45ms** |
| テスト通過 | **447/447** |

---

## アーキテクチャ

```
ユーザー入力
    ↓
自動分類（7 タイプ、4 階層）
    ↓
重要度スコアリング（confidence × type × recency × access）
    ↓
スマート保存（SQLite + FTS5、重複排除、TTL、暗号化）
    ↓
セマンティックリコール（FTS5 + 同義語 + スペル修正 + 言語間）
    ↓
コンテキスト注入（トークン予算、関連性ランキング）
    ↓
AI ツール（Cursor / Claude Code / 任意の MCP クライアント）
```

**3層分類戦略**：
```
ルールエンジン (60%+) → パターン分析 (30%) → セマンティック (10%)
     ↓                    ↓                    ↓
 ゼロコスト          ほぼゼロコスト        トークンコスト
```

---

## 高度な使い方

### Obsidian ナレッジベース

```python
from memory_classification_engine import CarryMem, ObsidianAdapter

cm = CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
cm.index_knowledge()
results = cm.recall_from_knowledge("Python デザインパターン")
```

### 非同期 API

```python
from memory_classification_engine import AsyncCarryMem

async with AsyncCarryMem() as cm:
    await cm.classify_and_remember("ダークモードが好き")
    memories = await cm.recall_memories("テーマ")
```

### JSON アダプター（SQLite 不要）

```python
from memory_classification_engine import CarryMem, JSONAdapter

cm = CarryMem(adapter=JSONAdapter("/path/to/memories.json"))
```

### 暗号化

```python
cm = CarryMem(encryption_key="my-secret-key")
# すべてのコンテンツは保存時に暗号化、読み取り時に復号
```

### メモリバージョニング

```python
cm.update_memory(key, "更新されたコンテンツ")     # バージョン 2 を作成
history = cm.get_memory_history(key)              # [v1, v2]
cm.rollback_memory(key, version=1)                # v1 に復元
```

### 他の AI へのアイデンティティエクスポート

```python
# AI アイデンティティをエクスポート
cm.export_profile(output_path="my_identity.json")

# 別のデバイスや AI ツールで
cm.import_memories(input_path="backup.json")
```

---

## ドキュメント

- [クイックスタートガイド](../QUICK_START_GUIDE.md)
- [アーキテクチャ](../ARCHITECTURE.md)
- [API リファレンス](../API_REFERENCE.md)
- [ユーザーストーリー](../USER_STORIES.md)
- [ロードマップ](../guides/ROADMAP.md)
- [コントリビューション](../../CONTRIBUTING.md)

---

## 誰のためのものか？

**開発者** — セッションを越えてユーザーを記憶する必要がある AI エージェントを構築する人

**パワーユーザー** — AI ツール（Cursor、Claude Code、Windsurf）に自分を記憶してほしい人

**チーム** — 共有メモリネームスペースを通じて組織のナレッジを共有する人

---

## プロジェクトステータス

**現在のバージョン**：v0.1.2
**テスト**：447/447 通過
**精度**：90.6%

**v0.8.x チェンジログ**：
- v0.1.2：アイデンティティレイヤー（whoami、プロファイルエクスポート）、競合差別化
- v0.8.1：ユーザー視点の CLI 改善（show/edit/clean、カラー出力、--force）
- v0.8.0：強化 CLI（19 コマンド）、TUI、MCP 設定、doctor、品質管理
- v0.7.0：MCP HTTP/SSE、JSON アダプター、非同期 API
- v0.6.0：暗号化、バックアップ、監査ログ
- v0.5.0：スマートコンテキスト注入、重要度スコアリング、キャッシュ、マージ、バージョニング

---

## コントリビューション

```bash
git clone https://github.com/lulin70/memory-classification-engine.git
cd carrymem
pip install -e ".[dev]"
pytest
```

詳細は [コントリビューションガイド](../../CONTRIBUTING.md) を参照してください。

---

## ライセンス

MIT ライセンス — 詳細は [LICENSE](../../LICENSE) を参照

---

**CarryMem — AI はあなたが誰かを覚える。データはあなただけのもの。** 🚀
