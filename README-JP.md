# Memory Classification Engine (MCE)

<p align="center">
  <strong>記憶分類ミドルウェア — AI Agent の「記憶セキュリティチェック」</strong><br>
  <sub>MCE は記憶を保存しません。MCE は<strong>何を記憶すべきか</strong>、<strong>どのタイプで記憶すべきか</strong>、<strong>どの階層に保存すべきか</strong>を教えます。<br>
  保存のことは、Supermemory / Mem0 / Obsidian / あなたのシステムに任せます。</sub>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README-CN.md">中文</a> ·
  <a href="./ROADMAP-JP.md">ロードマップ</a> ·
  <a href="./docs/user_guides/STORAGE_STRATEGY.md">ストレージ戦略</a> ·
  <a href="https://github.com/lulin70/memory-classification-engine/issues">問題報告</a>
</p>

---

## 問題：保存前に分類を行うシステムが存在しない

すべての AI 記憶システムには同じ盲点があります。

**Supermemory** はメッセージを受信 → そのまま保存。分類なし。
**Mem0** はメッセージを受信 → そのまま保存。分類なし。
**Claude Code CLAUDE.md** → 手動で何を書くか決定。構造なし。

それらはすべて **「どう保存するか」** に答えていますが、**「何を保存する価値があるか」** には答えていません。

結果：

| メッセージ | 保存すべき？ | 大多数のシステムの挙動 |
|-----------|-------------|---------------------|
| "ダブルクォートが好き" | はい — 好み | ✅ 保存（正しい） |
| "OK、いいね" | いいえ — 返事 | ❌ 保存（ノイズ） |
| "前のアプローチは複雑すぎた" | はい — 訂正 | ⚠️ 汎用要約として保存（タイプ情報喪失） |
| "今日はいい天気だね" | いいえ — 雑談 | ❌ 保存（検索を汚染） |

**60%以上のメッセージは保存されるべきではありません。** しかし現在のシステムは全て保存（ノイズ爆発）か、全て不保存（健忘）のどちらかです。

**MCE はその欠けていた前置フィルターです。**

---

## MCE の役割

MCE は**分類ミドルウェア**です。あなたの Agent と記憶システムの間に位置します：

```
あなたの AI Agent / Claude Code
        │  (生の会話メッセージ)
        ▼
┌───────────────────────────────┐
│     MCE (分類エンジン)        │
│                               │
│   入力: "Pythonではダブルクォー"
│       トが好き"               │
│                               │
│   出力: {                     │
│     should_remember: true,    │
│     type: "user_preference", │
│     confidence: 0.95,         │
│     tier: 2,                  │
│     suggested_action: "store" │
│   }                          │
└──────────────┬────────────────┘
               │  構造化 MemoryEntry (JSON)
               ▼
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 [Supermemory] [Mem0] [Obsidian] [独自DB]
    (クラウド)   (セルフホスト) (ローカル)   (カスタム)
```

**MCE は一つのことだけを極めています**：メッセージが記憶に値する情報を含んでいるかどうかを判断し、含まれている場合は7つのタイプの一つに分類して信頼度スコアを付けます。

**MCE はしません**：保存、検索、検索、削除、エクスポート、インポート、または記憶の呼び出し。これらは下流システムの責任です。

---

## なぜ分類が保存よりも重要なのか

### 論点1：60%フィルター

MCE の3層パイプラインは、高コストな処理に入る前に60%以上のメッセージをフィルタリングします：

```
入力メッセージ
       │
       ▼
┌─────────────────────┐   60%+ メッセージがここでフィルタ │ ゼロコスト
│ 第1層: ルール一致    │                            │ 正規表現 + キーワード
│   "覚える"、"常に"...│                            │ 決定的マッチ
└──────────┬──────────┘
           │ 非一致 (~40%)
           ▼
┌─────────────────────┐   30%+ メッセージがここで分類   │ 依然ゼロLLM
│ 第2層: パターン分析  │                            │ 会話構造
│   "3回目の拒否=好み" │                            │
└──────────┬──────────┘
           │ 曖昧 (~10%)
           ▼
┌─────────────────────┐   <10% メッセージがここに到達   │ LLMフォールバック
│ 第3層: セマンティック推論│                           │ エッジケースのみ
└─────────────────────┘
```

大多数のソリューションは第3層から始めます（全メッセージをLLMへ）。MCE は第1層から始めます。

**1,000メッセージあたりのコスト**：

| アプローチ | LLM呼出数 | コスト |
|-----------|----------|------|
| 全てLLMへ送信 | 1,000回 | $0.50 - $2.00 |
| **MCE（L1 + L2優先）** | **<100回** | **$0.05 - $0.20** |

### 論点2：タイプ付き記憶は生の要約より有用

```
メッセージ: "前のアプローチは複雑すぎた、もっと簡単にしよう"

MCEなし（生保存）:
  → 保存: "ユーザーがアプローチの複雑さについて議論"
  → 問題: 「拒絶」のコンテキストが失われる。「アプローチ」で検索するとノイズ

MCEあり（分類後）:
  → [訂正] "以前の複雑なアプローチを拒否、シンプルなものを好む"
  → 信頼度: 0.89 | 出所: パターン | 階層: エピソード的
  → メリット: 下流はタイプ別に異なるルーティングが可能
```

### 論点3：7タイプ > 1つのバケット

| タイプ | 例 | 重要な理由 |
|------|-----|-----------|
| **ユーザー好み** | "スペース而非Tabを好む" | 将来のコード生成全般に影響 |
| **訂正信号** | "違う、こうすべき" | 以前の事実/決定を上書きする必要あり |
| **事実宣言** | "従業員100名" | 検証可能な真理、稀に変化 |
| **決定記録** | "Redisをキャッシュに採用" | アーキテクチャがこうなった理由を説明 |
| **関係マッピング** | "Aliceがバックエンド担当" | 役割認識応答をサポート |
| **タスクパターン** | "デプロイ前に必ずテスト" | 自動化可能なワークフロールール |
| **感情マーカー** | "このワークフローはイライラする" | プロセスの痛点を識別 |

全てのメッセージが記憶を生むわけではありません。雑談（「OK」「ありがとう」）、応答、低信号コンテンツは自動的にフィルタリングされます。

---

## クイックスタート

```bash
pip install memory-classification-engine
```

データベース不要。API Key 不要。設定不要。純粋な分類。

### 30秒でメッセージ分類

```python
from memory_classification_engine import MemoryClassificationEngine

engine = MemoryClassificationEngine()

result = engine.process_message(
    "前のアプローチは複雑すぎた、もっと簡単にしよう"
)

if result.get('matches'):
    entry = result['matches'][0]
    print(f"タイプ: {entry.get('type')}")          # 'correction'
    print(f"信頼度: {entry.get('confidence')}")  # 0.89
    print(f"階層: {entry.get('tier')}")           # 3 (episodic)
    print(f"保存すべき: {entry.get('confidence', 0) > 0.5}")  # True
```

---

## MCP Server：2分でClaude Code統合

MCE は内蔵 MCP Server を搭載（**v0.2.0, プロダクション対応**）。MCE は完全にローカルで動作 —— **あなたのデータはマシンから出ません**。

> **ポジショニング**: MCE は**分類ミドルウェア**であり、完全な記憶システムではありません。MCP Server は分類ツールのみ公開；保存は下流システム（Supermemory、Mem0、Obsidian、または独自）に委譲します。

### 利用可能なツール (v0.2.0)

| ツール | ステータス | 説明 |
|-------|-----------|------|
| `classify_memory` | コア | メッセージ分類 → 構造化 MemoryEntry |
| `batch_classify` | コア | バッチ分類 |
| `mce_status` | コア | エンジン状態 |
| `store_memory` | ⚠️ v0.3非推奨 | 保存は下流アダプターへ移行 |
| `retrieve_memories` | ⚠️ v0.3非推奨 | 検索は下流システムへ |
| `get_memory_stats` | ⚠️ v0.3非推奨 | 統計は下流から取得 |
| `find_similar` | ⚠️ v0.3非推奨 | 類似検索は下流から |
| `export_memories` | ⚠️ v0.3非推奨 | エクスポートは下流が担当 |
| `import_memories` | ⚠️ v0.3非推奨 | インポートは下流へ |
| `mce_recall` | ⚠️ v0.3非推奨 | 呼び出しは下流（Supermemory recall()等）|
| `mce_forget` | ⚠️ v0.3非推奨 | 削除は下流経由 |

> **移行注意**: v0.3.0で非推奨ツールは削除されます。MCP Server は4ツールのみ公開：`classify_message`, `get_classification_schema`, `batch_classify`, `mce_status`

---

## FAQ

### MCE は Supermemory / Mem0 の代替になりますか？

**なりません。MCE はそれらと補完関係にあります。**

- **Supermemory / Mem0** = 倉庫（記憶の保存・検索）
- **MCE** = 倉庫入口のセキュリティチェック（何を入れてよいか判断）

両方同時に使用可能：MCE 分類 → Supermemory 保存 → Supermemory 呼び出し

### MCE に保存機能を入れない理由は？

1. **Supermemory は YC 出資 + Cloudflare インフラ + Benchmark #1**
2. **Mem0 は 18k Stars + ベクトル+グラフハイブリッド**
3. **しかし、どちらも保存前に分類を行っていません** ← これが MCE が埋めるギャップ

MCE は**世界最高の記憶分類器**を目指し、平均的な記憶システムを目指しません。

### データは安全ですか？

**安全です。** MCE は完全にローカルで動作。分類時に外部サーバーへデータは送信されません。分類後のデータの行方は、選択した下流システム次第 —— **あなたの管理下**にあります。

---

## インストール

```bash
pip install memory-classification-engine
```

**最小依存**: PyYAML のみ。他は全てオプション（ベクトルDB、グラフDB、LLM）。

---

## ライセンス

MIT

---

## リンク

- **リポジトリ**: [github.com/lulin70/memory-classification-engine](https://github.com/lulin70/memory-classification-engine)
- **ロードマップ**: [ROADMAP-JP.md](./ROADMAP-JP.md)
- **ストレージ戦略**: [STORAGE_STRATEGY.md](./docs/user_guides/STORAGE_STRATEGY.md)
- **戦略合意**: [MCP_POSITIONING_CONSENSUS_v3.md](./docs/consensus/MCP_POSITIONING_CONSENSUS_v3.md)
