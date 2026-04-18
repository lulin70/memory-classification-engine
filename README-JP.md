# Memory Classification Engine

<p align="center">
  <strong>すべてを覚えるのではなく、覚えるべきものだけを覚える。</strong><br>
  <sub>AI Agent 用リアルタイム記憶分類エンジン。60%+ ゼロ LLM コスト。</sub>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README-ZH.md">中文</a> ·
  <a href="./ROADMAP-JP.md">ロードマップ</a> ·
  <a href="https://github.com/lulin70/memory-classification-engine/issues">問題報告</a>
</p>

---

## 問題：Agent はすべて忘れるか、すべて覚えすぎるか

すべての AI Agent が同じ記憶のジレンマに直面しています。

選択 A：**何も保存しない。** 新しいセッション毎にゼロから開始。ユーザーは何度も同じことを言う。Agent は過去と同じミスを繰り返す。

選択 B：**すべて保存する。** 会話全体を要約してベクトル DB に放り込む。最初は問題ない。50 セッション後、検索結果は曖昧なノイズだらけになる。コストはメッセージ数に比例（1 メッセージ = 1 回 LLM 呼び出し）。

根本原因：**ほとんどのシステムは、保存する前に分類を行わない。** ユーザーの好み（「ダブルクォートを使う」）、決定（「PostgreSQL を採用」）、雑談（「いい天気ですね」）を区別せず、一括で保存している。

## MCE の違うところ

MCE は保存前に**すべてのメッセージをリアルタイム分類**します：

```
メッセージ：「前のアプローチは複雑すぎる、もっとシンプルにしよう」

従来のシステム：
  → 要約の一部として保存：「アプローチの複雑さについて議論」
  → 文脈喪失：これは以前の決定に対する**拒絶**である
  → 検索結果：他 50 の要約に埋もれ、関連性が低い

MCE：
  → [correction] 「以前の複雑なアプローチを拒否、簡素化を希望」
  → decision_001 に自動リンク（元のアプローチ）
  → 信頼度: 0.89 | 出所: パターン分析 | 階層: エピソード
  → LLM コスト: $0（Layer 2 で処理）
```

同じメッセージ。従来システムはノイズを保存。MCE は**実行可能な、型付きの、相互リンクされた記憶**を LLM コストゼロで保存。

**1,000 メッセージあたりのコスト：**

| アプローチ | LLM 呼び出し | コスト |
|-----------|-------------|--------|
| 全量要約 | 1,000 | $0.50 - $2.00 |
| **MCE** | **<100** | **$0.05 - $0.20** |

---

## 三層パイプライン：安い方から、高い方へ

```
受信メッセージ
       │
       ▼
┌─────────────────────┐   60%+ のメッセージ     │  ゼロコスト
│ Layer 1: ルールマッチ│   ここで処理完了       │  正規表現 + キーワード
│   "覚える", "今後は" │                         │  決定的判定
└──────────┬──────────┘
           │ 未マッチ
           ▼
┌─────────────────────┐   30%+ のメッセージ     │  まだ LLM 不要
│ Layer 2: 構造分析    │   ここで処理完了        │  会話パターン認識
│                     │   「3回目の訂正＝好み」  │
└──────────┬──────────┘
           │ 未マッチ
           ▼
┌─────────────────────┐   <10% のメッセージ      │  LLM フォールバック
│ Layer 3: 意味推論    │   ここにのみ到達        │  曖昧なエッジケース
└─────────────────────┘
```

ほとんどのソリューションは Layer 3 から始まります。MCE は Layer 1 から始め、必要時のみエスカレートします。これが 60%+ の分類がゼロコストである理由です。

---

## クイックスタート

```bash
pip install memory-classification-engine
```

データベース不要。API キー不要。設定不要。そのまま使えます。

### 30 秒で試す

```python
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

# シナリオ 1: ユーザーが前のアプローチを否定（暗黙の訂正信号）
engine.process_message(
    "前のアプローチは複雑すぎる、もっとシンプルにしよう"
)
# → [correction] 以前の複雑なアプローチを拒否
#   信頼度: 0.89, 出所: pattern, 階層: episodic
#   自動リンク: decision_001

# シナリオ 2: 不満の裏にある繰り返し発生する痛点
engine.process_message(
    "デプロイ前に必ずテストしなければならない、このプロセスはとても退屈"
)
# → [sentiment_marker] デプロイプロセスへの不満
#   暗示パターン: デプロイ前テスト（自動抽出）

# シナリオ 3: 1 文でのチーム分担
engine.process_message(
    "Alice がバックエンド担当、Bob がフロントエンド、私が全体監督"
)
# → [relationship] Alice→バックエンド, Bob→フロント, User→監督
#   信頼度: 0.95, 階層: semantic
```

### 適応型検索モード (v2.0)

MCE v2.0 では、各種シナリオに対応する 3 種類の検索モードを導入しました：

```python
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

# コンパクトモード：キーワードのみマッチ、レイテンシ <10ms、LLM コストゼロ
memories = engine.retrieve_memories("デプロイチェックリスト", limit=5,
                                     retrieval_mode='compact')

# バランスドモード：デフォルト — セマンティックソート＋最適化パイプライン（推奨）
memories = engine.retrieve_memories("デプロイチェックリスト", limit=5,
                                     retrieval_mode='balanced')

# コンプリヘンシブモード：深層分析＋関連付け＋複合スコアリング
memories = engine.retrieve_memories("デプロイチェックリスト", limit=5,
                                     retrieval_mode='comprehensive',
                                     include_associations=True)
```

| モード | レイテンシ | 利用シーン |
|------|----------|----------|
| `compact` | <10ms | 高頻度検索、キーワード中心のクエリ |
| `balanced` | ~15-50ms | 汎用（デフォルト） |
| `comprehensive` | 50-200ms | 深層調査、決定レビュー |

### クロスセッション記憶リコール

ユーザーが実際に感じる価値：新しい会話を開始したとき、Agent が重要なことを**覚えている**こと。

```python
from memory_classification_engine import MemoryOrchestrator

memory = MemoryOrchestrator()

# ... 1 週間使用後 ...

# 新規セッション開始時、関連記憶をロード
memories = memory.recall(context="coding", limit=5)
for m in memories:
    print(f"[{m['type']}] {m['content']} (信頼度: {m['confidence']}, 出所: {m['source']})")
# 出力:
# [user_preference] ダブルクォートを使用 (信頼度: 0.95, 出所: rule)
# [decision] Python 採用、Go ではない (信頼度: 0.91, 出所: rule)
# [relationship] Alice はバックエンド API 担当 (信頼度: 0.88, 出所: semantic)
# [correction] 過度な設計禁止、シンプルに (信頼度: 0.89, 出所: pattern)
# [fact_declaration] 本番環境は Ubuntu 22.04 (信頼度: 0.92, 出所: rule)
#
# 統計: 5 件ロード | 12 件ノイズフィルタリング | LLM 呼び出し 0 回
```

---

## MCP Server：Claude Code へ 2 分で統合

MCE には MCP サーバーが組み込まれています（**プロダクション v1.0.0**）。Claude Code / Cursor など MCP 対応ツールで MCE を使う最速の方法です。

```bash
cd mce-mcp
python3 server.py
# MCP サーバー起動: http://localhost:9001
```

Claude Code 設定 (`~/.claude/settings.json`) に追加：

```json
{
  "mcpServers": {
    "mce": {
      "command": "python3",
      "args": ["/path/to/mce-mcp/server.py"]
    }
  }
}
```

利用可能ツール：`classify_message`、`retrieve_memories`、`store_memory`、`search_memories`、`get_memory_stats`、`delete_memory`、`update_memory`、`export_memories`、`import_memories`。

Claude Code で送信したメッセージがすべて自動分類・保存されます。新規セッションごとに構造化された記憶サマリーがロードされます。

詳細なドキュメントは [API Reference](./docs/api/API_REFERENCE_V1.md) を参照してください。

---

## 何を分類するか：7 種類の記憶タイプ

| タイプ | 例 | 保存先 |
|-------|-----|--------|
| **user_preference** | 「スペースを好む」 | Tier 2: 手続き型 |
| **correction** | 「こうじゃなくて、あっちだ」 | Tier 3: エピソード |
| **fact_declaration** | 「社員は 100 名」 | Tier 3: エピソード |
| **decision** | 「キャッシュは Redis にしよう」 | Tier 3: エピソード |
| **relationship** | 「Alice がバックエンド担当」 | Tier 4: 意味 |
| **task_pattern** | 「デプロイ前に必ずテスト」 | Tier 2: 手続き型 |
| **sentiment_marker** | 「このワークフローはイライラする」 | Tier 3: エピソード |

すべてのメッセージが記憶を生成するわけではありません。挨拶、確認語（「OK」「ありがとう」）、低信号コンテンツは保存前にフィルタリングされます。

---

## 自己進化：パターンがルールに昇格

エンジンを使えば使うほど、コストは下がり精度は上がります。

| 時間 | Layer 1 (ルール) | Layer 2 (パターン) | Layer 3 (LLM) | コスト/千件 |
|------|------------------|-------------------|---------------|-----------|
| 1 週目 | 30% | 40% | 30% | $0.15 |
| 4 週目 | 50%（+20 自動ルール） | 35% | 15% | $0.08（-47%） |
| 3 ヶ月目 | 65%（+50 自動ルール） | 25% | 10% | $0.05（-67%） |

自動生成ルール例：

```yaml# システム初期ルール（初日から）：
- pattern: "覚える.*好む"
  type: user_preference

# 1 ヶ月使用後に自動学習：
- pattern: "複雑.*シンプル"
  type: correction
  source: learned_from_user_behavior

- pattern: "毎回.*面倒"
  type: sentiment_marker
  source: learned_from_user_behavior
```

あなたの使用パターンが無料の分類ルールになります。手動チーニング不要です。

### フィードバックループ自動化 (v2.0)

MCE v2.0 には、分類精度を継続的に向上させる自動フィードバックループが組み込まれています：

- **FeedbackAnalyzer**: ユーザーの訂正からパターンを検出（最低 3 回出現）
- **RuleTuner**: 検出されたパターンからルール提案を生成
- **自動適用**: 信頼度が閾値を超えたルールが自動的に適用される

```python
result = engine.process_feedback(memory_id="mem_001",
                                  correction_type="wrong_type",
                                  suggested_type="decision")
# → パターン検出: ユーザーによる episodic→decision 訂正が 3 回目
# → ルール提案生成済み、自動適用待機中（信頼度: 0.85）
```

### モデル蒸留インターフェース (v2.0)

コスト最適化が必要な本番環境デプロイ向け：

```python
from memory_classification_engine.layers.distillation import DistillationRouter

router = DistillationRouter()
request = ClassificationRequest(message="コードスタイルに関するユーザー好み")

# 推定信頼度に基づいてルーティング：
# >0.85 → embedding のみ（ゼロ LLM）
# 0.5-0.85 → 弱モデル（低コスト）
# <0.5 → 強モデル（高精度）
result = router.classify(request)
```

---

## 他ソリューションとの比較

| 機能 | Mem0 | MemGPT | LangChain Memory | **MCE** |
|------|------|--------|------------------|---------|
| 書き込みタイミング | 会話後一括抽出 | コンテキストウィンドウ | 手動/Hooks | **リアルタイム逐条分類** |
| 記憶分類 | 基本タグ | なし | なし | **7 種類 + 三層パイプライン** |
| 記憶階層 | 単層（ベクトル） | 2 層（メモリ+ディスク） | 単層（セッション） | **4 層（作業/手続き/エピソード/意味）** |
| 忘却機構 | なし | 受動的オーバーフロー | なし | **能動的減衰 + Nudge レビュー** |
| 学習能力 | 静的 | なし | なし | **パターンのルール自動昇格 + フィードバックループ** |
| LLM コスト | 1 メッセージあたり | 中程度 | 低 | **60%+ ゼロコスト分類** |
| クロスセッション | エクスポートのみ | なし | なし | **構造化移行標準** |
| MCP 対応 | なし | なし | なし | **内蔵 MCP サーバー (v1.0.0 プロダクション)** |
| 高レベル API | なし | なし | 基本 | **MemoryOrchestrator** |
| 検索モデル | 全内容 | 全内容 | 全内容 | プログレッシブ開示 | **3 適応モード + 型付き記憶** |
| フィードバックループ | なし | なし | なし | **自動パターン検出・ルールチューニング** |

---

## 四層記憶ストレージ

| 階層 | 名前 | ストレージ | ライフサイクル |
|------|------|----------|-------------|
| T1 | 作業記憶 | コンテキストウィンドウ | 当該セッションのみ |
| T2 | 手続き型 | 設定ファイル / システムプロンプト | 長期、常時ロード |
| T3 | エピソード | ベクトルDB（ChromaDB / SQLite） | 重み付け減衰 |
| T4 | 意味 | 知識グラフ（Neo4j / メモリ） | 長期、相互リンク |

コア依存関係：**PyYAML のみ**。ベクトル DB、グラフ DB、LLM はすべてオプション拡張です。

---

## パフォーマンス

ベンチマークデータは `benchmarks/baseline_benchmark.py` からのもの（Phase 1 最適化後）：

| 指標 | 最適化前 | 最適化後 | 改善幅 |
|------|---------|---------|--------|
| `process_message` P99 レイテンシ | 5,669 ms | 1,452 ms | **-74%** |
| `retrieve_memories` 長文 P99 | 85 ms | 50 ms | **-41%** |
| キャッシュヒット率（ウォームアップ後） | 0% | 97.83% | **+97.83pp** |
| テストスイート | 661 テスト | 696 テスト | **+35 テスト** |
| メッセージ処理（Layer 1/2） | ~10ms | ~10ms | ベースライン |
| 検索レイテンシ（バランスドモード） | ~15ms | ~15ms | ベースライン |
| 同時スループット | 626 msg/s | 626 msg/s | ベースライン |
| メモリ使用量 | <100MB | <100MB | ベースライン |
| LLM 呼び出し比率 | <10% | <10% | ベースライン |
| 記憶圧縮率 | 87-90% ノイズ削減 | 87-90% | ベースライン |

**主要最適化項目：**
- FAISS 次元不一致修正（毎回の呼び出しでの AssertionError を解消）
- SmartCache 書き換え：OrderedDict ベースの O(1) LRU 追放 + スタートアップウォームアップ
- 並列クエリ：ThreadPoolExecutor によるストレージ階層間並列取得
- ハッシュインデックス：O(1) の `get_memory` 検索
- バッチベクトルエンコーディング + 事前計算ソートキーによるセマンティックランキング

---

## プロジェクト構造

```
memory-classification-engine/
├── mce-mcp/                         # MCP Server（Claude Code / Cursor 統合）
│   ├── server.py                    #   サーバー入口（v1.0.0 プロダクション）
│   ├── tools/                       #   MCP ツール実装
│   └── config.yaml                  #   サーバー設定
│
├── src/memory_classification_engine/
│   ├── engine.py                    # コアコーディネータ（適応型検索モード）
│   ├── layers/
│   │   ├── rule_matcher.py          #   Layer 1: ルールマッチ
│   │   ├── pattern_analyzer.py      #   Layer 2: 構造分析
│   │   ├── semantic_classifier.py   #   Layer 3: LLM フォールバック
│   │   ├── feedback_loop.py         #   v2.0: 自動フィードバック＆ルールチューニング
│   │   └── distillation.py          #   v2.0: モデル蒸留ルーティング
│   ├── storage/
│   │   └── tier3.py                 #   FAISS ベクトルインデックス（次元安全）
│   ├── coordinators/
│   │   └── storage_coordinator.py   #   並列クエリ + ハッシュインデックス
│   ├── utils/
│   │   └── memory_manager.py        #   SmartCache（OrderedDict + ウォームアップ）
│   ├── orchestrator.py              # MemoryOrchestrator 高レベル API
│   └── utils/
│
├── benchmarks/
│   ├── baseline_benchmark.py        # パフォーマンス測定ツール
│   └── final_results.json           # 最適化後のベンチマークデータ
│
├── examples/                        # 実行可能なサンプル
├── tests/                           # テストスイート（696 テスト全パス）
├── config/rules.yaml                # 分類ルール設定
├── setup.py                         # PyPI パッケージ設定
└── README.md
```

---

## インストール

```bash
# コア（分類エンジンのみ）
pip install memory-classification-engine

# RESTful API サーバー付き
pip install -e ".[api]"

# LLM セマンティック分類付き（Layer 3）
pip install -e ".[llm]"
export MCE_LLM_API_KEY="your-key"
export MCE_LLM_ENABLED=true

# scikit-learn インストール（ベクトルエンコーディング最適化用）
pip install scikit-learn

# テスト実行
pip install -e ".[testing]"
pytest
```

---

## ライセンス

MIT

---

## リンク

- リポジトリ: [github.com/lulin70/memory-classification-engine](https://github.com/lulin70/memory-classification-engine)
- ロードマップ: [ROADMAP-JP.md](./ROADMAP-JP.md)
- API ドキュメント: [docs/api/API_REFERENCE_V1.md](./docs/api/API_REFERENCE_V1.md)
- 最適化ロードマップ: [docs/OPTIMIZATION_ROADMAP_V1.md](./docs/OPTIMIZATION_ROADMAP_V1.md)
- Claude Code MCP 設定: [docs/claude_code_mcp_config.md](./docs/claude_code_mcp_config.md)
- Issues / Discussions
