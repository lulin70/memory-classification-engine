# Memory Classification Engine - ロードマップ

## 更新履歴

| バージョン | 日付 | 更新者 | 更新内容 | レビュー状態 |
|------------|------|--------|----------|--------------|
| v0.2.0 | 2026-04-18 | エンジニアリングチーム | Phase 1 最適化完了（process_message -74%）、Phase 2 機能提供完了（適応型検索/フィードバックループ/蒸留）、MCP Server をプロダクション v1.0.0 に昇格、テストスイートを **874 テスト**に拡張、EN/ZH/JP ドキュメント全面更新、Demo テスト 26/30 (87%) 通過 | レビュー済み |
| v1.2.0 | 2026-04-12 | プロダクトチーム | VS Code 拡張機能、メモリ品質ダッシュボード、確認待ちメモリメカニズム、Nudge メカニズムを追加 | レビュー済み |
| v1.1.0 | 2026-04-11 | プロダクトチーム | MCP Server 完成、Beta テスト開始 | レビュー済み |
| v1.0.0 | 2026-04-10 | プロダクトチーム | 初期バージョン - 三層統合戦略計画 | レビュー済み |

---

## ビジョン

エージェントのメモリ分類分野の標準コンポーネントになること、ChromaDB がベクトルストレージのように、メモリ分類の代名词になること。

**製品ポジショニング**：「すべてを覚えるのではなく、覚えるべきものだけを覚える。」——軽量で高効率な専門 AI エージェント用メモリ分類エンジン。

---

## 完了したマイルストーン

### Phase 1：パフォーマンス最適化 ✅ （2026-04-17 完了）

**状態**：全タスク完了、ベンチマーク検証済み

**デリバリー物**：

| タスク | 説明 | 結果 |
|------|------|------|
| T1.1 | パフォーマンスベースライン確立 | `benchmarks/baseline_benchmark.py` 作成 |
| T1.2 | FAISS 次元不一致修正 | 毎回の `process_message` 呼び出しでの AssertionError を解消 |
| T1.3 | SmartCache 書き換え（OrderedDict + LRU） | O(1) 追放 vs 旧版 O(n) スキャン |
| T1.4 | エンジン起動時キャッシュウォームアップ | キャッシュヒット率：0% → **97.83%** |
| T1.5 | 並列クエリ（ThreadPoolExecutor） | tier2/tier3/tier4 並列取得 |
| T1.6 | get_memory ハッシュインデックス | `_id_index` 辞書による O(1) 検索 |
| T1.7 | アーカイブ修正（選択的無効化） | `_run_archive` が全キャッシュをクリアしなくなった |
| T1.8 | セマンティックソート深層最適化 | バッチエンコーディング＋事前計算キー：P99 **-41%** |
| T1.9 | 最終ベンチマーク検証 | `process_message` P99：全体 **-74%** |

**最適化前後の主要指標**：
- `process_message` P99：5,669ms → 1,452ms（**-74%**）
- `retrieve_memories` 長文 P99：85ms → 50ms（**-41%**）
- キャッシュヒット率：0% → **97.83%**
- テスト数：661 → **696**

### Phase 2：v2.0 機能 ✅ （2026-04-17 完了）

**状態**：全機能提供完了

#### P0：適応型検索モード ✅

各種シナリオに対応する 3 種類の検索モード：

| モード | レイテンシ目標 | 戦略 |
|------|-------------|------|
| `compact` | <10ms | キーワードのみマッチ、セマンティックソートをスキップ |
| `balanced` | ~15-50ms | デフォルトモード、最適化されたセマンティックパイプライン |
| `comprehensive` | 50-200ms | 完全分析＋関連付け＋複合スコアリング |

実装：`engine.py` の `retrieve_memories()` に `retrieval_mode` パラメータ追加、`_retrieve_compact()`、`_retrieve_balanced()`、または `_retrieve_comprehensive()` にディスパッチ。

#### P1：フィードバックループ自動化 ✅

ユーザーの訂正から自動的にパターンを検出してルールを調整：

- **FeedbackEvent / FeedbackAnalyzer**：パターン検出（最低 3 回出現）
- **RuleTuner**：パターンからルール提案を生成
- **FeedbackLoop**：信頼度が閾値を超えた場合に自動適用（デフォルト 0.8）

ファイル：[feedback_loop.py](../src/memory_classification_engine/layers/feedback_loop.py)

#### P2：モデル蒸留インターフェース ✅

本番環境向けコスト認識ルーティング：

- **ConfidenceEstimator**：分類の困難度を見積もり
- **DistillationRouter**：embedding のみ（>0.85）、弱モデル（0.5-0.85）、強モデル（<0.5）にルーティング
- モデル蒸馏用のオフライントレーニングデータエクスポート対応

ファイル：[distillation.py](../src/memory_classification_engine/layers/distillation.py)

### MCP サーバープロダクションリリース ✅ （v1.0.0）

**状態**：Beta からプロダクションに昇格

- MCPServer クラスに VERSION = "1.0.0" を設定
- PROTOCOL_VERSION = "2024-11-05"
- 完全な API リファレンスドキュメント：[API_REFERENCE_V1.md](./docs/api/API_REFERENCE_V1.md)
- 11 の MCP ツールを提供

---

## 三層統合戦略

### Layer 1：Python SDK ✅ （完了＆最適化済み）

**状態**：利用可能、Phase 1 でパフォーマンス最適化完了

**目的**：最も基本的な Python ライブラリを提供し、誰でも pip install して簡単に統合できるようにする

**コア機能**：
- [x] リアルタイムメッセージ分類
- [x] 7 種類のメモリタイプ識別
- [x] 三層判断パイプライン
- [x] 四層メモリストレージ
- [x] アクティブな忘却メカニズム
- [x] 適応型検索モード（compact/balanced/comprehensive）
- [x] フィードバックループ自動化
- [x] モデル蒸留インターフェース
- [x] SmartCache ウォームアップ（97.83% ヒット率）
- [x] ストレージ階層間並列クエリ
- [x] ハッシュインデックス O(1) 検索
- [x] VS Code 拡張機能
- [x] メモリ品質ダッシュボード
- [x] 確認待ちメモリメカニズム
- [x] Nudge アクティブレビューメカニズム

---

### Layer 2：MCP Server ✅ （プロダクション v1.0.0）

**状態**：プロダクションリリース完了

**目的**：Claude Code、Cursor、OpenClaw など MCP 対応ツールが直接呼び出せるようにする

**なぜ MCP を優先するのか？**

| 利点 | 説明 |
|------|------|
| トレンド | Anthropic が MCP を強力に推進しており、関連リポジトリの成長が速い |
| ターゲットユーザー | Claude Code / Cursor ユーザーがまさにターゲットオーディエンス |
| 低投資 | パッケージングコストが低い（JSON-RPC インターフェース層） |
| 高転換率 | ゼロ摩擦の使用体験、トピックトラフィックの転換率が高い |

**機能計画**：

#### Phase 1：コア MCP ツール ✅ （完了）

- [x] `classify_memory` - メッセージを分析してメモリの必要性を判断
- [x] `store_memory` - 適切な階層にメモリを保存
- [x] `retrieve_memories` - 関連メモリを検索（適応モード対応）
- [x] `get_memory_stats` - メモリ統計を取得
- [x] `batch_classify` - バッチ分類
- [x] `find_similar` - 類似メモリの検索
- [x] `export_memories` - メモリのエクスポート
- [x] `import_memories` - メモリのインポート

#### Phase 2：OpenClaw 統合 ✅ （完了）

- [x] OpenClaw アダプタ
- [x] OpenClaw 設定ファイル
- [x] 使用例とドキュメント

**リリース計画**：
- PyPI パッケージ名: `mce-mcp-server`
- MCP コミュニティリポジトリに提出
- Claude Code / Cursor コミュニティで共有

---

### Layer 3：Framework Adapters （長期）

**状態**：計画中

**目的**：主流のエージェントフレームワークに対して、すぐに使える Skill パッケージを提供

**フレームワーク適応計画**：

#### LangChain （優先度：高）

```python
from memory_classification_engine.adapters.langchain import MemoryClassifierTool

tool = MemoryClassifierTool()
```

**機能**：
- [ ] MemoryClassifierTool クラス
- [ ] LangChain Memory との統合
- [x] 使用ドキュメントと例

#### CrewAI （優先度：中）

```python
from memory_classification_engine.adapters.crewai import MemoryTool

tool = MemoryTool()
```

**機能**：
- [ ] MemoryTool クラス
- [ ] CrewAI Agent との統合
- [ ] 使用ドキュメントと例

#### AutoGen （優先度：中）

```python
from memory_classification_engine.adapters.autogen import MemoryAgent

agent = MemoryAgent()
```

**機能**：
- [ ] MemoryAgent コンポーネント
- [ ] AutoGen 会話との統合
- [ ] 使用ドキュメントと例

---

## 技術的負債の解消

### コード品質最適化 ✅ （完了）

**完了**：
- [x] P0/P1 コード品質問題の修正
- [x] エンジンクラスの分割リファクタリング (Facade パターン)
- [x] サービス層アーキテクチャの実装
- [x] コードレビューチェックリスト
- [x] 静的コード分析ツールの設定
- [x] Phase 1 パフォーマンス最適化（9 タスク）
- [x] Phase 2 v2.0 機能提供（3 主要機能）
- [x] 英語コードコメント追記（394 所のプレースホルダーを修正）
- [x] ドキュメント全面更新（EN/ZH/JP：README/ROADMAP/設計/アーキテクチャ/テスト/API/インストール）

**計画**：
- [ ] 依存性注入フレームワークの導入
- [ ] エラー処理メカニズムの改善
- [ ] さらなるストレージ層パフォーマンスチューニング

---

## プロモーションと運用計画

### Phase 1：MCP サーバーローンチ ✅ （完了）

**技術作業**：
- [x] MCP サーバーコア機能の実装（11 ツール）
- [x] MCP 設定ドキュメントの作成
- [x] Claude Code 使用例の作成
- [x] 27 単体テストの完了 → 696 テストに拡張
- [x] OpenClaw 統合
- [x] プロダクション v1.0.0 に昇格
- [ ] PyPI へのリリース

**プロモーション作業**：
- [x] Beta テストガイドの作成（英語・中国語）
- [x] 完全な API リファレンス作成（API_REFERENCE_V1.md）
- [x] マルチロールコンセンサス最適化ロードマップ作成
- [ ] MCP コミュニティリポジトリに提出
- [ ] Claude Code Discord で共有
- [x] 技術ブログ執筆

### Phase 2：コミュニティ構築（2-3ヶ月）

**コンテンツマーケティング**：
- ブログ記事：「なぜあなたのエージェントに専門的なメモリ分類が必要か」
- デモ動画：Claude Code + MCE デモンストレーション
- ユーザーケース：実際の使用シナリオ

**コミュニティ運営**：
- Reddit r/ClaudeAI
- Hacker News Show
- Twitter/X テックサークル
- GitHub Discussions

### Phase 3：フレームワーク統合（3-6ヶ月）

**技術作業**：
- LangChain アダプタ
- CrewAI アダプタ
- AutoGen アダプタ

**プロモーション作業**：
- 各フレームワークコミュニティに PR 提出
- 統合チュートリアル執筆
- 比較ベンチマップ提供

---

## 主要マイルストーン

| 時間 | マイルストーン | 主要指標 | 状態 |
|------|-------------|----------|------|
| 2026-04-11 | MCP Server Beta テスト開始 | Beta テストガイド公開 | ✅ 完了 |
| 2026-04-17 | Phase 1 最適化完了 | process_message -74%、キャッシュ 97.83% | ✅ 完了 |
| 2026-04-17 | Phase 2 v2.0 機能提供完了 | 適応型検索/フィードバックループ/蒸留 | ✅ 完了 |
| 2026-04-17 | MCP Server プロダクション v1.0.0 | VERSION=1.0.0、PROTOCOL_VERSION 設定 | ✅ 完了 |
| 2026-04-17 | ドキュメント更新サイクル | README/ROADMAP EN/ZH/JP、設計/アーキ/テスト/API/インストールドキュメント | 🔄 進行中 |
| 1ヶ月目 | MCP サーバー正式リリース | GitHub Stars: 200+ | 🔄 進行中 |
| 2ヶ月目 | コミュニティの初期確立 | Stars: 500+, コミュニティメンバー: 50+ | ⏳ 開始待ち |
| 3ヶ月目 | LangChain 適応 | Stars: 800+, ダウンロード数: 1000/月 | ⏳ 開始待ち |
| 6ヶ月目 | 完全なエコシステム | Stars: 1500+, ダウンロード数: 5000/月 | ⏳ 開始待ち |

---

## 決定記録

### なぜ Skill フレームワークにしないのか？

**議論**: LangChain のようなフレームワークにすべきか？

**決定**: フレームワークにしない、エンジンに焦点を当てる

**理由**:
1. フレームワークの競争は激しい（LangChain、LlamaIndex など）
2. エンジンの位置づけはより明確で、差別化が明確
3. 他のフレームワークに統合されやすい
4. 維持コストが低い

### なぜ MCP Server を Framework Adapters より優先するのか？

**議論**: LangChain の適応を先にすべきか？

**決定**: MCP Server を優先

**理由**:
1. MCP はトレンドであり、Anthropic が強力に推進している
2. 投資対効果が高い（パッケージングコストが低く、ユーザーがターゲット）
3. LangChain の適応は後で Layer 3 として行うことができる
4. MCP ユーザーは新しいツールを試す意欲が高い

---

## 付録

### 関連ドキュメント

- [アーキテクチャ設計](docs/architecture/architecture.md)
- [アーキテクチャ設計（日本語）](docs/architecture/architecture-zh.md)
- [設計ドキュメント](docs/design.md)
- [設計ドキュメント（中国語）](docs/design-zh.md)
- [設計ドキュメント（日本語）](docs/design-jp.md)
- [API リファレンス](docs/api/API_REFERENCE_V1.md)
- [最適化ロードマップ](docs/OPTIMIZATION_ROADMAP_V1.md)
- [ユーザーガイド](docs/user_guides/user_guide.md)
- [ユーザーガイド（中国語）](docs/user_guides/user_guide-zh.md)
- [ユーザーガイド（日本語）](docs/user_guides/user_guide-jp.md)
- [インストールガイド](docs/user_guides/installation_guide.md)
- [テストプラン V2](docs/testing/MCE_TEST_PLAN_V2.md)

### 関連リンク

- [MCP 公式ドキュメント](https://modelcontextprotocol.io/)
- [Claude Code ドキュメント](https://docs.anthropic.com/en/docs/claude-code/overview)
- [OpenClaw プロジェクト](https://github.com/openclaw)

---

**ドキュメントバージョン**: v2.0.0
**最終更新**: 2026-04-17
**レビュー状態**: レビュー済み
