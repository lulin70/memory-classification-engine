# Memory Classification Engine - ロードマップ

## 更新履歴

| バージョン | 日付 | 更新者 | 更新内容 | レビュー状態 |
|------------|------|--------|----------|--------------|
| v1.2.0 | 2026-04-12 | プロダクトチーム | VS Code 拡張機能、メモリ品質ダッシュボード、確認待ちメモリメカニズム、Nudge メカニズムを追加 | レビュー済み |
| v1.1.0 | 2026-04-11 | プロダクトチーム | MCP Server 完成、Beta テスト開始 | レビュー済み |
| v1.0.0 | 2026-04-10 | プロダクトチーム | 初期バージョン - 三層統合戦略計画 | レビュー済み |

---

## 🎯 ビジョン

エージェントのメモリ分類分野の標準コンポーネントになること、ChromaDB がベクトルストレージのように、メモリ分類の代名词になること。

---

## 三層統合戦略

### Layer 1: Python SDK ✅ (完成)

**状態**: 使用可能

**目標**: 最も基本的な Python ライブラリを提供し、誰でも pip install して簡単に統合できるようにする

**コア機能**:
- [x] リアルタイムメッセージ分類
- [x] 7 種類のメモリタイプ識別
- [x] 三層判断パイプライン
- [x] 四層メモリストレージ
- [x] アクティブな忘却メカニズム
- [x] VS Code 拡張機能
- [x] メモリ品質ダッシュボード
- [x] 確認待ちメモリメカニズム
- [x] Nudge アクティブレビューメカニズム

**次の最適化**:
- [ ] API ドキュメントの改善
- [ ] より多くの使用例の追加
- [ ] パフォーマンス最適化

---

### Layer 2: MCP Server ⭐ (Beta テスト中)

**状態**: ✅ コア機能完成、Beta テスト進行中

**目標**: Claude Code、Cursor、OpenClaw など MCP 対応ツールが直接呼び出せるようにする

**なぜ MCP を優先するのか？**

| 利点 | 説明 |
|------|------|
| トレンド | Anthropic が MCP を強力に推進しており、関連リポジトリの成長が速い |
| ターゲットユーザー | Claude Code / Cursor ユーザーがまさにターゲットオーディエンス |
| 低投資 | パッケージングコストが低い（JSON-RPC インターフェース層） |
| 高転換率 | ゼロ摩擦の使用体験、トピックトラフィックの転換率が高い |

**機能計画**:

#### Phase 1: コア MCP ツール ✅ (完成)

- [x] `classify_memory` - メッセージを分析してメモリの必要性を判断
- [x] `store_memory` - 適切な階層にメモリを保存
- [x] `retrieve_memories` - 関連するメモリを検索
- [x] `get_memory_stats` - メモリ統計を取得
- [x] `batch_classify` - バッチ分類
- [x] `find_similar` - 類似メモリの検索
- [x] `export_memories` - メモリのエクスポート
- [x] `import_memories` - メモリのインポート

#### Phase 2: OpenClaw 統合 ✅ (完成)

- [x] OpenClaw アダプタ
- [x] OpenClaw 設定ファイル
- [x] 使用例とドキュメント

**技術ソリューション**:

```python
# MCP Server アーキテクチャ
mcp-server/
├── src/
│   └── mce_mcp_server/
│       ├── server.py      # MCP Server メインエントリー
│       ├── tools.py       # ツール定義
│       └── config.py      # 設定管理
├── pyproject.toml
└── README.md
```

**リリース計画**:
- PyPI パッケージ名: `mce-mcp-server`
- MCP コミュニティリポジトリに提出
- Claude Code / Cursor コミュニティで共有

---

### Layer 3: Framework Adapters (長期)

**状態**: 計画中

**目標**: 主流のエージェントフレームワークに対して、すぐに使える Skill パッケージを提供

**フレームワーク適応計画**:

#### LangChain (優先度: 高)

```python
from memory_classification_engine.adapters.langchain import MemoryClassifierTool

tool = MemoryClassifierTool()
```

**機能**:
- [ ] MemoryClassifierTool クラス
- [ ] LangChain Memory との統合
- [ ] 使用ドキュメントと例

#### CrewAI (優先度: 中)

```python
from memory_classification_engine.adapters.crewai import MemoryTool

tool = MemoryTool()
```

**機能**:
- [ ] MemoryTool クラス
- [ ] CrewAI Agent との統合
- [ ] 使用ドキュメントと例

#### AutoGen (優先度: 中)

```python
from memory_classification_engine.adapters.autogen import MemoryAgent

agent = MemoryAgent()
```

**機能**:
- [ ] MemoryAgent コンポーネント
- [ ] AutoGen 会話との統合
- [ ] 使用ドキュメントと例

---

## 技術的負債の解消

### コード品質最適化 (継続中)

**完成**:
- [x] P0/P1 コード品質問題の修正
- [x] エンジンクラスの分割リファクタリング (Facade パターン)
- [x] サービス層アーキテクチャの実装
- [x] コードレビューチェックリスト
- [x] 静的コード分析ツールの設定

**進行中**:
- [ ] 単体テストカバレッジの改善
- [ ] パフォーマンスベンチマーク
- [ ] ドキュメントの改善

**計画**:
- [ ] 依存性注入フレームワークの導入
- [ ] エラー処理メカニズムの改善
- [ ] ストレージ層パフォーマンスの最適化

---

## プロモーションと運用計画

### Phase 1: MCP Server ローンチ ✅ (進行中)

**技術作業**:
- [x] MCP Server コア機能の実装 (8 つのツール)
- [x] MCP 設定ドキュメントの作成
- [x] Claude Code 使用例の作成
- [x] 27 個の単体テストの完成
- [ ] OpenClaw 統合
- [ ] PyPI へのリリース

**プロモーション作業**:
- [x] Beta テストガイドの作成 (英語と中国語)
- [ ] MCP コミュニティリポジトリに提出
- [ ] Claude Code Discord で共有
- [ ] 技術ブログの執筆

### Phase 2: コミュニティ構築 (2-3ヶ月)

**コンテンツマーケティング**:
- ブログ記事: "なぜあなたのエージェントに専門的なメモリ分類が必要か"
- デモ動画: Claude Code + MCE デモンストレーション
- ユーザーケース: 実際の使用シナリオ

**コミュニティ運営**:
- Reddit r/ClaudeAI
- Hacker News Show
- Twitter/X テックサークル
- GitHub Discussions

### Phase 3: フレームワーク統合 (3-6ヶ月)

**技術作業**:
- LangChain アダプタ
- CrewAI アダプタ
- AutoGen アダプタ

**プロモーション作業**:
- 各フレームワークコミュニティに PR を提出
- 統合チュートリアルの執筆
- 比較ベンチマークの提供

---

## 主要マイルストーン

| 時間 | マイルストーン | 主要指標 | 状態 |
|------|-------------|----------|------|
| 2026-04-11 | MCP Server Beta テスト開始 | Beta テストガイド公開 | ✅ 完成 |
| 1ヶ月目 | MCP Server 正式リリース | GitHub Stars: 200+ | 🔄 進行中 |
| 2ヶ月目 | コミュニティの初期確立 | Stars: 500+, コミュニティメンバー: 50+ | ⏳ 開始待ち |
| 3ヶ月目 | LangChain 適応 | Stars: 800+, ダウンロード数: 1000/月 | ⏳ 開始待ち |
| 6ヶ月目 | 完全なエコシステム | Stars: 1500+, ダウンロード数: 5000/月 | ⏳ 開始待ち |

---

## 決定記録

### なぜ Skill フレームワークにしないのか？

**議論**: LangChain のようなフレームワークにするべきか？

**決定**: フレームワークにしない、エンジンに焦点を当てる

**理由**:
1. フレームワークの競争は激しい（LangChain、LlamaIndex など）
2. エンジンの位置づけはより明確で、差別化が明確
3. 他のフレームワークに統合されやすい
4. 維持コストが低い

### なぜ MCP Server を Framework Adapters より優先するのか？

**議論**: LangChain の適応を先にするべきか？

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
- [API ドキュメント](docs/api/api.md)
- [ユーザーガイド](docs/user_guides/user_guide.md)
- [コード品質修正記録](docs/code_quality_fixes.md)

### 関連リンク

- [MCP 公式ドキュメント](https://modelcontextprotocol.io/)
- [Claude Code ドキュメント](https://docs.anthropic.com/en/docs/claude-code/overview)
- [OpenClaw プロジェクト](https://github.com/openclaw)

---

**ドキュメントバージョン**: v1.2.0  
**最終更新**: 2026-04-12  
**レビュー状態**: レビュー済み