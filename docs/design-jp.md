# メモリー分類エンジン - 詳細設計文書

## 1. システムアーキテクチャ設計

### 1.1 全体アーキテクチャ

メモリー分類エンジンは、モジュール式の階層化アーキテクチャ設計を採用しており、以下のコンポーネントで構成されています：

```
┌─────────────────────┐
│     外部システム     │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│    API/SDK インターフェース層│
│ ┌─────────────────┐ │
│ │ Python SDK      │ │
│ ├─────────────────┤ │
│ │ REST API        │ │
│ ├─────────────────┤ │
│ │ MCP Server      │ │
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  高度なラッパー層   │
│ ┌─────────────────┐ │
│ │ MemoryOrchestrator││
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   コアエンジン      │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  多層判断パイプライン  │
│ ┌─────────────────┐ │
│ │ ルールマッチング層  │ │
│ ├─────────────────┤ │
│ │ パターン分析層    │ │
│ ├─────────────────┤ │
│ │ 意味推論層       │ │
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  メモリー管理       │
│ ┌─────────────────┐ │
│ │ 重複排除         │ │
│ ├─────────────────┤ │
│ │ 忘却メカニズム     │ │
│ ├─────────────────┤ │
│ │ ナッジメカニズム   │ │
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  メモリー品質評価    │
│ ┌─────────────────┐ │
│ │ 使用追跡         │ │
│ ├─────────────────┤ │
│ │ フィードバック分析  │ │
│ ├─────────────────┤ │
│ │ 品質計算         │ │
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  メモリー移行システム  │
│ ┌─────────────────┐ │
│ │ データエクスポート  │ │
│ ├─────────────────┤ │
│ │ データインポート   │ │
│ └─────────────────┘ │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  ストレージ層       │
│ ┌─────────────────┐ │
│ │ 作業メモリー      │ │
│ ├─────────────────┤ │
│ │ 手続きメモリー     │ │
│ ├─────────────────┤ │
│ │ エピソードメモリー  │ │
│ ├─────────────────┤ │
│ │ 意味メモリー      │ │
│ └─────────────────┘ │
└─────────────────────┘
```

### 1.2 コアコンポーネントの説明

1. **API/SDK インターフェース層**：外部システムとメモリー分類エンジン間のインターフェースを提供し、Python SDK、REST API、MCP Serverをサポートします。
   - **Python SDK**：コアプログラミングインターフェースで、完全な機能アクセスを提供します。
   - **REST API**：HTTPベースのインターフェースで、クロス言語統合をサポートします。
   - **MCP Server**：MCPプロトコルを実装し、Claude Code、Cursorなどのツールとの統合をサポートします。

2. **高度なラッパー層**：
   - **MemoryOrchestrator**：ワンストップのメモリー管理ソリューションで、分類、ストレージ、検索、忘却、品質評価、移行機能を統合した統一された高レベルインターフェースを提供します。

3. **コアエンジン**：各モジュールの作業を調整し、外部リクエストを処理するシステム全体のハブです。

4. **多層判断パイプライン**：
   - **ルールマッチング層**：正規表現とキーワードマッチングに基づいて、明確なユーザー信号を識別します。
   - **パターン分析層**：対話の相互作用パターンを分析し、繰り返しの質問、計画の承認/拒否パターンなどを識別します。
   - **意味推論層**：LLMを呼び出して意味分析を行い、複雑なメモリー認識を処理します。

5. **メモリー管理**：
   - **重複排除と競合検出**：重複メモリーを避け、メモリーの競合を処理します。
   - **忘却メカニズム**：時間、頻度、重要性に基づく重み付き減衰アルゴリズム。
   - **ナッジメカニズム**：メモリーの定期的な確認と検証システムで、定期的にメモリーをチェックおよび調整します。

6. **メモリー品質評価**：
   - **使用追跡**：メモリーの使用頻度とシナリオを記録します。
   - **フィードバック分析**：ユーザーからのメモリーに関するフィードバックを収集および分析します。
   - **品質計算**：多次元指標に基づいてメモリーの品質スコアを計算します。

7. **メモリー移行システム**：
   - **データエクスポート**：メモリーを標準JSON形式にエクスポートします。
   - **データインポート**：標準JSON形式からメモリーをインポートします。

8. **ストレージ層**：
   - **作業メモリー**：メモリー内ストレージで、セッション終了後にクリアされます。
   - **手続きメモリー**：ファイルシステムベースのストレージで、ユーザーの嗜好や行動ルールに適しています。
   - **エピソードメモリー**：SQLiteベースのストレージで、決定記録やタスクパターンに適しています。
   - **意味メモリー**：SQLiteベースのストレージで、事実の宣言や関係情報に適しています。

## 2. コアモジュール設計

### 2.1 コアエンジンモジュール

#### 2.1.1 機能設計
- 初期化と設定管理
- ユーザーメッセージの処理、多層判断パイプラインの調整
- メモリーのストレージと検索の管理
- 外部インターフェースの提供

#### 2.1.2 クラス設計

```python
class MemoryClassificationEngine:
    def __init__(self, config_path=None):
        # エンジンを初期化し、設定をロード
        pass
    
    def process_message(self, message, context=None):
        # ユーザーメッセージを処理し、メモリー分類結果を返す
        pass
    
    def retrieve_memories(self, query, limit=5):
        # クエリに基づいて関連するメモリーを検索
        pass
    
    def manage_memory(self, action, memory_id, data=None):
        # メモリーを管理（表示、編集、削除）
        pass
    
    def get_stats(self):
        # システム統計情報を取得
        pass
```

### 2.2 多層判断パイプラインモジュール

#### 2.2.1 ルールマッチング層

**機能**：ルール設定に基づいて明確なユーザー信号を識別します。

**設計**：
- ルール設定：YAML形式で、正規表現とキーワードマッチングをサポート
- ルールロード：設定ファイルからルールをロード
- ルールマッチング：ルールをユーザー入力に適用し、メモリータイプを識別

**ルール設定例**：
```yaml
rules:
  - pattern: "記憶して(ください|ね)"
    memory_type: user_preference
    tier: 2
    action: extract_following_content
  
  - pattern: "(しないで|しないでください|やめて)"
    memory_type: user_preference
    tier: 2
    action: extract_following_content
  
  - pattern: "(違う|間違ってる|そうじゃない|間違えた|私の言ったのは)"
    memory_type: correction
    tier: 3
    action: extract_surrounding_context
```

#### 2.2.2 パターン分析層

**機能**：対話構造を分析し、パターンを識別します。

**設計**：
- 対話状態追跡：対話状態とパターンを追跡
- 重複検出：繰り返しの質問とタスクパターンを検出
- 計画の承認/拒否識別：ユーザーによる計画の承認または拒否を識別

#### 2.2.3 意味推論層

**機能**：LLMを使用して意味分析を行い、複雑なメモリー認識を処理します。

**設計**：
- LLM呼び出し：軽量LLMを呼び出して意味分析を行う
- プロンプト設計：効果的なプロンプトを設計し、LLMにメモリー分類を指示
- コスト制御：LLM呼び出し頻度を制限し、結果をキャッシュ

**プロンプト例**：
```
あなたはメモリー分類器です。以下の会話の断片を分析し、長期的に記憶する価値のある情報があるかどうかを判断してください。

メモリーの種類は次のとおりです：
- user_preference: ユーザーが表現した嗜好または習慣
- fact_declaration: ユーザーが述べた客観的な事実
- decision: 明確な決定または達成された結論
- relationship: 人、チーム、組織間の関係
- task_pattern: 繰り返されるタスクの種類
- sentiment_marker: ユーザーのあるトピックに対する感情的傾向
- correction: ユーザーによる以前の出力の訂正

会話に記憶する価値のある情報がない場合は、空を返してください。

現在の会話：
{conversation_snippet}

既知のユーザーメモリー：
{existing_memory_summary}

以下のフィールドを含むJSON形式で出力してください：
- has_memory: boolean
- memory_type: string (列挙値)
- content: string (メモリー内容、簡潔で正確)
- tier: int (2=手続きメモリー, 3=エピソードメモリー, 4=意味メモリー)
- confidence: float (0.0-1.0)
- reasoning: string (簡単な判断理由)
```

### 2.3 メモリー管理モジュール

#### 2.3.1 重複排除と競合検出

**機能**：メモリーの重複と競合を検出し処理します。

**設計**：
- 重複検出：内容の類似性とメモリータイプに基づいて重複メモリーを検出
- 競合検出：新旧メモリー間の競合を検出
- 競合解決：タイムスタンプと信頼度に基づく競合解決メカニズムを提供

#### 2.3.2 忘却メカニズム

**機能**：時間、頻度、重要性に基づいて低価値メモリーを自動的に減衰させ淘汰します。

**設計**：
- メモリー重み計算：時間減衰、アクセス頻度、信頼度に基づいてメモリー重みを計算
- メモリーアーカイブ：メモリーの重みが閾値を下回るとアーカイブとしてマーク
- メモリークリーンアップ：定期的にアーカイブされたメモリーをクリーンアップ

**重み計算式**：
```
メモリー重み = 信頼度 × 新鮮度スコア × 頻度スコア

新鮮度スコア = exp(-λ × 最終アクセスからの日数)  # 指数減衰
頻度スコア = log(1 + アクセス回数)            # 対数成長、限界減少
```

### 2.4 ストレージ層モジュール

#### 2.4.1 作業メモリー

**機能**：現在のセッションのコンテキスト情報を保存します。

**設計**：
- メモリー内ストレージ：Pythonの辞書またはキューを使用したストレージ
- セッション管理：セッション終了後に自動的にクリア
- サイズ制限：過度なメモリー使用を避けるための最大容量を設定

#### 2.4.2 手続きメモリー

**機能**：ユーザーの嗜好、行動ルールなどの固定情報を保存します。

**設計**：
- ファイルストレージ：YAML/JSONファイルを使用したストレージ
- 階層的ロード：グローバル、プロジェクトレベル、ローカルレベルの設定をサポート
- フォーマット設計：読み取りと変更が容易な構造化フォーマット

**ストレージフォーマット例**：
```yaml
user_preferences:
  - id: "pref_001"
    content: "シングルクォートではなくダブルクォートを使用する"
    created_at: "2026-04-03T10:00:00Z"
    updated_at: "2026-04-03T10:00:00Z"
    confidence: 1.0
    source: "rule:0"
```

#### 2.4.3 エピソードメモリー

**機能**：決定記録、タスクパターンなどの時間関連情報を保存します。

**設計**：
- SQLiteストレージ：SQLiteデータベースを使用したストレージ
- テーブル構造設計：メモリーのメタデータとコンテンツを含む
- 検索最適化：時間とコンテンツに基づく検索をサポート

**テーブル構造設計**：
```sql
CREATE TABLE episodic_memories (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_accessed TEXT NOT NULL,
    access_count INTEGER DEFAULT 0,
    confidence REAL NOT NULL,
    source TEXT NOT NULL,
    context TEXT,
    status TEXT DEFAULT 'active'
);
```

#### 2.4.4 意味メモリー

**機能**：事実の宣言、関係情報などの構造化知識を保存します。

**設計**：
- SQLiteストレージ：SQLiteデータベースを使用したストレージ
- 関係モデル：エンティティ-関係-属性モデルを使用
- クエリ最適化：複雑な関係クエリをサポート

**テーブル構造設計**：
```sql
CREATE TABLE semantic_entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE semantic_relationships (
    id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    confidence REAL NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES semantic_entities(id),
    FOREIGN KEY (object_id) REFERENCES semantic_entities(id)
);
```

### 2.5 高度なラッパーモジュール

#### 2.5.1 MemoryOrchestrator

**機能**：ワンストップのメモリー管理ソリューションを提供し、分類、ストレージ、検索、忘却、品質評価、移行機能を統合します。

**設計**：
- 統一インターフェース：簡潔なAPIを提供し、基盤の複雑さを隠す
- 機能統合：学習、想起、忘却、検索、品質評価、移行などのすべてのコア機能を統合
- エラー処理：包括的な例外捕捉とエラー処理
- ロギング：詳細な操作ログ

**コアメソッド**：
```python
class MemoryOrchestrator:
    def learn(self, message, context=None, execution_context=None):
        # 新しいメモリーを学習
        pass
    
    def recall(self, query, memory_type=None, limit=10):
        # 関連するメモリーを想起
        pass
    
    def forget(self, memory_id, action='decrease_weight', weight_adjustment=0.1):
        # メモリーを忘却または調整
        pass
    
    def search(self, search_term, memory_types=None, min_confidence=0.5, limit=20):
        # 高度な検索
        pass
    
    def get_memory_quality(self, memory_id):
        # メモリーの品質を取得
        pass
    
    def generate_quality_report(self, days=30):
        # 品質レポートを生成
        pass
    
    def export_memories(self, include_metadata=True):
        # メモリーをエクスポート
        pass
    
    def import_memories(self, json_str, validate_checksum=True):
        # メモリーをインポート
        pass
```

### 2.6 メモリー品質評価モジュール

**機能**：メモリーの使用状況、有効性、価値を追跡し、品質評価とレポートを提供します。

**設計**：
- データ追跡：メモリーの使用とユーザーフィードバックを記録
- 多次元評価：使用頻度、成功率、フィードバックスコア、新鮮度、多様性に基づいて品質を計算
- レポート生成：品質レポートと低価値メモリーレポートを生成
- リアルタイム更新：メモリーが使用されると自動的に使用統計を更新

**コアメソッド**：
```python
class MemoryQualityManager:
    def track_memory_usage(self, memory_id, query, result=True):
        # メモリー使用を追跡
        pass
    
    def track_feedback(self, memory_id, feedback, context=None):
        # ユーザーフィードバックを追跡
        pass
    
    def calculate_memory_quality(self, memory_id, memory):
        # メモリーの品質を計算
        pass
    
    def generate_low_value_report(self, threshold=0.3, days=30):
        # 低価値メモリーレポートを生成
        pass
    
    def generate_quality_report(self, days=30):
        # 品質レポートを生成
        pass
```

### 2.7 メモリー移行モジュール

**機能**：メモリーのエクスポートとインポートを実装し、セッション間、エージェント間のメモリー移行をサポートします。

**設計**：
- 標準フォーマット：クロスプラットフォーム互換性を確保するための統一JSONフォーマットを定義
- データ検証：データ整合性を確保するためのチェックサムの生成と検証
- ファイルサポート：ファイルへのエクスポートとファイルからのインポートをサポート
- エラー処理：包括的な例外捕捉とエラー処理

**コアメソッド**：
```python
class MemoryMigrationManager:
    def export_memories(self, memories, include_metadata=True):
        # メモリーを標準フォーマットにエクスポート
        pass
    
    def import_memories(self, json_str, validate_checksum=True):
        # 標準フォーマットからメモリーをインポート
        pass
    
    def export_to_file(self, memories, file_path, include_metadata=True):
        # メモリーをファイルにエクスポート
        pass
    
    def import_from_file(self, file_path, validate_checksum=True):
        # ファイルからメモリーをインポート
        pass
    
    def validate_export_data(self, json_str):
        # エクスポートデータの有効性を検証
        pass
```

### 2.8 MCP Server モジュール

**機能**：MCP (Model Context Protocol) サーバーを実装し、Claude Code、Cursorなどのツールとの統合をサポートします。

**設計**：
- HTTPサーバー：標準ライブラリのhttp.serverに基づいて実装
- ツール定義：3つのコアツールを提供：classify_message、retrieve_memories、manage_forgetting
- 設定管理：設定ファイルを通じてカスタムサーバー設定をサポート
- エラー処理：包括的な例外捕捉とエラーレスポンス

**コアツール**：
1. **classify_message**：メッセージを分析し、メモリーが必要かどうかを判断
2. **retrieve_memories**：関連するメモリーを検索
3. **manage_forgetting**：メモリーの忘却プロセスを管理

## 3. データモデル設計

### 3.1 メモリーメタデータモデル

```json
{
  "id": "mem_20260403_001",
  "type": "user_preference",
  "tier": 2,
  "content": "シングルクォートではなくダブルクォートを使用する",
  "created_at": "2026-04-03T10:00:00Z",
  "updated_at": "2026-04-03T10:00:00Z",
  "last_accessed": "2026-04-03T10:30:00Z",
  "access_count": 5,
  "confidence": 1.0,
  "source": "rule:0",
  "context": "コードスタイルの議論中にユーザーが言及",
  "status": "active"
}
```

### 3.2 メモリータイプ列挙

```python
MEMORY_TYPES = {
    "user_preference": "ユーザーの嗜好",
    "correction": "訂正",
    "fact_declaration": "事実の宣言",
    "decision": "決定",
    "relationship": "関係",
    "task_pattern": "タスクパターン",
    "sentiment_marker": "感情マーカー"
}
```

### 3.3 メモリー階層列挙

```python
MEMORY_TIERS = {
    1: "作業メモリー",
    2: "手続きメモリー",
    3: "エピソードメモリー",
    4: "意味メモリー"
}
```

## 4. API インターフェース設計

### 4.1 Python SDK インターフェース（レイヤー 1）

```python
class MemoryClassificationEngine:
    def __init__(self, config_path=None):
        """エンジンを初期化"""
        pass
    
    def process_message(self, message, context=None):
        """ユーザーメッセージを処理し、メモリー分類結果を返す"""
        pass
    
    def retrieve_memories(self, query, limit=5):
        """クエリに基づいて関連するメモリーを検索"""
        pass
    
    def manage_memory(self, action, memory_id, data=None):
        """メモリーを管理（表示、編集、削除）"""
        pass
    
    def get_stats(self):
        """システム統計情報を取得"""
        pass
    
    def export_memories(self, format="json"):
        """メモリーデータをエクスポート"""
        pass
    
    def import_memories(self, data, format="json"):
        """メモリーデータをインポート"""
        pass
```

### 4.2 MCP Server インターフェース（レイヤー 2）⭐ 最近の重点

#### 4.2.1 MCP Server アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server モジュール                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  server.py - MCP Server メインエントリ              │   │
│  │  • MCP Server を初期化                                   │   │
│  │  • すべてのツールを登録                                    │   │
│  │  • JSON-RPC リクエストを処理                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  tools.py - ツール定義                                 │   │
│  │  • 8つのコアツール定義                                    │   │
│  │  • 入力/出力 Schema 定義                             │   │
│  │  • パラメータ検証                                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  handlers.py - リクエストハンドラ                      │   │
│  │  • 各ツールのビジネスロジック                             │   │
│  │  • エンジン SDK を呼び出す                               │   │
│  │  • エラー処理                                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2.2 MCP ツールの詳細設計

**ツール 1: classify_memory**

```python
{
    "name": "classify_memory",
    "description": "メッセージを分析し、メモリーが必要かどうかを判断",
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "ユーザーメッセージの内容"
            },
            "context": {
                "type": "string",
                "description": "会話のコンテキスト（オプション）"
            }
        },
        "required": ["message"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "matched": {
                "type": "boolean",
                "description": "メモリータイプが一致したかどうか"
            },
            "memory_type": {
                "type": "string",
                "enum": ["user_preference", "correction", "fact_declaration", 
                        "decision", "relationship", "task_pattern", "sentiment_marker"],
                "description": "メモリータイプ"
            },
            "tier": {
                "type": "integer",
                "enum": [2, 3, 4],
                "description": "メモリー階層"
            },
            "content": {
                "type": "string",
                "description": "抽出されたメモリー内容"
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "信頼度"
            },
            "reasoning": {
                "type": "string",
                "description": "判断理由"
            }
        }
    }
}
```

**ツール 2: store_memory**

```python
{
    "name": "store_memory",
    "description": "メモリーを適切な階層に保存",
    "inputSchema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "メモリー内容"
            },
            "memory_type": {
                "type": "string",
                "enum": ["user_preference", "correction", "fact_declaration", 
                        "decision", "relationship", "task_pattern", "sentiment_marker"],
                "description": "メモリータイプ"
            },
            "tier": {
                "type": "integer",
                "enum": [2, 3, 4],
                "description": "メモリー階層（オプション、デフォルトで自動的に決定）"
            },
            "context": {
                "type": "string",
                "description": "コンテキスト情報（オプション）"
            }
        },
        "required": ["content", "memory_type"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "memory_id": {
                "type": "string",
                "description": "メモリーID"
            },
            "stored": {
                "type": "boolean",
                "description": "保存に成功したかどうか"
            },
            "tier": {
                "type": "integer",
                "description": "実際の保存階層"
            }
        }
    }
}
```

**ツール 3: retrieve_memories**

```python
{
    "name": "retrieve_memories",
    "description": "関連するメモリーを検索",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "検索内容"
            },
            "limit": {
                "type": "integer",
                "default": 5,
                "description": "結果の数量制限"
            },
            "tier": {
                "type": "integer",
                "enum": [2, 3, 4],
                "description": "指定階層（オプション）"
            }
        },
        "required": ["query"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "memories": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "type": {"type": "string"},
                        "tier": {"type": "integer"},
                        "content": {"type": "string"},
                        "confidence": {"type": "number"},
                        "created_at": {"type": "string"},
                        "relevance_score": {"type": "number"}
                    }
                }
            }
        }
    }
}
```

**ツール 4: get_memory_stats**

```python
{
    "name": "get_memory_stats",
    "description": "メモリー統計情報を取得",
    "inputSchema": {
        "type": "object",
        "properties": {
            "tier": {
                "type": "integer",
                "enum": [2, 3, 4],
                "description": "指定階層（オプション、指定しない場合はすべての階層を返す）"
            }
        }
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "total_memories": {"type": "integer"},
            "by_tier": {
                "type": "object",
                "properties": {
                    "2": {"type": "integer"},
                    "3": {"type": "integer"},
                    "4": {"type": "integer"}
                }
            },
            "by_type": {
                "type": "object",
                "additionalProperties": {"type": "integer"}
            },
            "storage_size": {"type": "string"}
        }
    }
}
```

#### 4.2.3 MCP Server 設定

**claude_desktop_config.json:**

```json
{
  "mcpServers": {
    "memory-classification-engine": {
      "command": "python",
      "args": ["-m", "mce_mcp_server"],
      "env": {
        "MCE_CONFIG_PATH": "/path/to/config.yaml",
        "MCE_DATA_PATH": "/path/to/data"
      }
    }
  }
}
```

**Cursor MCP 設定:**

```json
{
  "mcpServers": {
    "memory-classification-engine": {
      "command": "python",
      "args": ["-m", "mce_mcp_server"],
      "env": {
        "MCE_CONFIG_PATH": "/path/to/config.yaml",
        "MCE_DATA_PATH": "/path/to/data"
      }
    }
  }
}
```

### 4.3 OpenClaw CLI インターフェース（レイヤー 2）

#### 4.3.1 CLI コマンド設計

```bash
# インストール
pip install mce-openclaw

# メモリーを分類
mce-openclaw classify --message "ダブルクォートを使用するのが好きです" --context "コードスタイルの議論"

# メモリーを保存
mce-openclaw store --content "ダブルクォートを使用する" --type user_preference --tier 2

# メモリーを検索
mce-openclaw retrieve --query "コードスタイル" --limit 5

# 統計情報を取得
mce-openclaw stats [--tier 2]

# バッチ分類
mce-openclaw batch-classify --file messages.json

# 類似を見つける
mce-openclaw find-similar --content "コードスタイルの嗜好" --threshold 0.8

# メモリーをエクスポート
mce-openclaw export --format json --output memories.json [--tier 3]

# メモリーをインポート
mce-openclaw import --file memories.json --format json
```

#### 4.3.2 OpenClaw 設定ファイル (.clawrc)

```yaml
# .clawrc - OpenClaw 設定ファイル
version: "1.0"

tools:
  - name: mce_classify
    description: メッセージを分析し、メモリーが必要かどうかを判断
    command: mce-openclaw classify
    args:
      - name: message
        type: string
        required: true
        description: ユーザーメッセージの内容
      - name: context
        type: string
        required: false
        description: 会話のコンテキスト

  - name: mce_store
    description: メモリーを適切な階層に保存
    command: mce-openclaw store
    args:
      - name: content
        type: string
        required: true
        description: メモリー内容
      - name: type
        type: string
        required: true
        description: メモリータイプ
      - name: tier
        type: integer
        required: false
        description: メモリー階層

  - name: mce_retrieve
    description: 関連するメモリーを検索
    command: mce-openclaw retrieve
    args:
      - name: query
        type: string
        required: true
        description: 検索内容
      - name: limit
        type: integer
        required: false
        default: 5
        description: 結果の数量

  - name: mce_stats
    description: メモリー統計情報を取得
    command: mce-openclaw stats
    args:
      - name: tier
        type: integer
        required: false
        description: 指定階層
```

### 4.4 フレームワークアダプターインターフェース（レイヤー 3）

#### 4.4.1 LangChain アダプター

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional

class ClassifyMemoryInput(BaseModel):
    message: str = Field(description="ユーザーメッセージの内容")
    context: Optional[str] = Field(default=None, description="会話のコンテキスト")

class MemoryClassifierTool(BaseTool):
    """LangChain メモリー分類ツール"""
    
    name: str = "memory_classifier"
    description: str = "ユーザーメモリーを分類および保存"
    args_schema: type[BaseModel] = ClassifyMemoryInput
    
    def __init__(self, config_path: str = None):
        super().__init__()
        from memory_classification_engine import MemoryClassificationEngine
        self.engine = MemoryClassificationEngine(config_path)
    
    def _run(self, message: str, context: Optional[str] = None) -> dict:
        """ツールを実行"""
        return self.engine.process_message(message, context)
    
    async def _arun(self, message: str, context: Optional[str] = None) -> dict:
        """非同期実行"""
        return self._run(message, context)
```

#### 4.4.2 CrewAI アダプター

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional

class StoreMemoryInput(BaseModel):
    content: str = Field(description="メモリー内容")
    memory_type: str = Field(description="メモリータイプ")
    tier: Optional[int] = Field(default=None, description="メモリー階層")

class MemoryTool(BaseTool):
    """CrewAI メモリー管理ツール"""
    
    name: str = "memory_tool"
    description: str = "ユーザーメモリーを管理 - 分類、保存、検索"
    args_schema: Type[BaseModel] = StoreMemoryInput
    
    def __init__(self, config_path: str = None):
        super().__init__()
        from memory_classification_engine import MemoryClassificationEngine
        self.engine = MemoryClassificationEngine(config_path)
    
    def _run(self, content: str, memory_type: str, tier: Optional[int] = None) -> dict:
        """メモリーを保存"""
        return self.engine.store_memory(content, memory_type, tier)
```

#### 4.4.3 AutoGen アダプター

```python
from autogen import ConversableAgent
from typing import Dict, Any, Optional

class MemoryAgent(ConversableAgent):
    """メモリー機能を備えた AutoGen エージェント"""
    
    def __init__(
        self,
        name: str,
        config_path: Optional[str] = None,
        system_message: Optional[str] = None,
        **kwargs
    ):
        # メモリーエンジンを初期化
        from memory_classification_engine import MemoryClassificationEngine
        self.memory_engine = MemoryClassificationEngine(config_path)
        
        # メモリー機能を備えたシステムメッセージを構築
        enhanced_system_message = self._build_system_message(system_message)
        
        super().__init__(
            name=name,
            system_message=enhanced_system_message,
            **kwargs
        )
    
    def _build_system_message(self, base_message: Optional[str]) -> str:
        """強化されたシステムメッセージを構築"""
        memory_capabilities = """
あなたはメモリー分類エンジンにアクセスできます。これは以下のことができます：
1. ユーザーメッセージを分類して記憶する価値のある重要な情報を識別
2. メモリーを適切な階層に保存
3. コンテキストに基づいて関連するメモリーを検索

これらの機能を使用して、パーソナライズされた応答を提供してください。
"""
        if base_message:
            return f"{base_message}\n\n{memory_capabilities}"
        return memory_capabilities
    
    def process_message_with_memory(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """メッセージを処理し、自動的にメモリーを分類"""
        # まず関連するメモリーを検索
        memories = self.memory_engine.retrieve_memories(message)
        
        # 現在のメッセージを分類
        classification = self.memory_engine.process_message(message, context)
        
        return {
            "memories": memories,
            "classification": classification
        }
```

### 4.2 REST API インターフェース

#### 4.2.1 メッセージの処理
- **URL**: `/api/message`
- **メソッド**: POST
- **リクエストボディ**:
  ```json
  {
    "message": "記憶してください、私はコードにダッシュを使用したくないです",
    "context": {}
  }
  ```
- **レスポンス**:
  ```json
  {
    "matched": true,
    "memory_type": "user_preference",
    "tier": 2,
    "content": "コードにダッシュを使用したくない",
    "confidence": 1.0,
    "source": "rule:0"
  }
  ```

#### 4.2.2 メモリーの検索
- **URL**: `/api/memories`
- **メソッド**: GET
- **クエリパラメータ**:
  - `query`: 検索クエリ
  - `limit`: 結果の数量制限
- **レスポンス**:
  ```json
  {
    "memories": [
      {
        "id": "mem_20260403_001",
        "type": "user_preference",
        "tier": 2,
        "content": "コードにダッシュを使用したくない",
        "confidence": 1.0,
        "source": "rule:0"
      }
    ]
  }
  ```

#### 4.2.3 メモリーの管理
- **URL**: `/api/memories/{id}`
- **メソッド**: GET, PUT, DELETE
- **リクエストボディ** (PUT):
  ```json
  {
    "content": "コードにダッシュとセミコロンを使用したくない",
    "confidence": 1.0
  }
  ```
- **レスポンス**:
  ```json
  {
    "success": true,
    "memory": {
      "id": "mem_20260403_001",
      "type": "user_preference",
      "tier": 2,
      "content": "コードにダッシュとセミコロンを使用したくない",
      "confidence": 1.0,
      "source": "rule:0"
    }
  }
  ```

## 5. テスト計画設計

### 5.1 単体テスト

**テスト目標**：各モジュールの機能的な正確さを検証します。

**テスト内容**：
- コアエンジンの初期化と設定
- ルールマッチング層のルールロードとマッチング
- パターン分析層のパターン認識
- 意味推論層のLLM呼び出しと結果解析
- メモリー管理の重複排除と競合検出
- 忘却メカニズムの重み計算とメモリーアーカイブ
- ストレージ層の読み書き操作

**新規 - レイヤー 2 単体テスト**：
- MCP Server の初期化
- MCP ツールのパラメータ検証
- MCP ツールのビジネスロジック
- OpenClaw CLI コマンドの解析
- OpenClaw CLI パラメータの検証

**テストツール**：
- pytest
- mock ライブラリ（LLM呼び出しのシミュレーション）
- pytest-asyncio（MCP Server 非同期テスト）

### 5.2 統合テスト

**テスト目標**：モジュール間の統合が正常であることを検証します。

**テスト内容**：
- 完全なメモリー分類プロセス
- メモリーのストレージと検索プロセス
- メモリー管理操作
- API インターフェース呼び出し

**新規 - レイヤー 2/3 統合テスト**：
- MCP Server とエンジン SDK の統合
- MCP JSON-RPC プロトコルの互換性
- Claude Code MCP クライアントの互換性
- Cursor MCP クライアントの互換性
- OpenClaw CLI とエンジン SDK の統合
- OpenClaw 設定ファイルの解析
- LangChain アダプターの統合
- CrewAI アダプターの統合
- AutoGen アダプターの統合

**テストツール**：
- pytest
- requests（REST API のテスト）
- mcp.client（MCP クライアントのテスト）
- subprocess（CLI のテスト）

### 5.3 パフォーマンステスト

**テスト目標**：システムのパフォーマンスとリソース使用状況を検証します。

**テスト内容**：
- メモリー分類の応答時間
- メモリー検索の応答時間
- システムの同時リクエスト処理能力
- メモリー使用状況
- ストレージ使用状況

**テストツール**：
- pytest-benchmark
- timeit
- memory-profiler

### 5.4 ユーザー受け入れテスト

**テスト目標**：システムがユーザー要件を満たしているかどうかを検証します。

**テスト内容**：
- メモリー分類の正確さ
- メモリー検索の関連性
- メモリー管理の使いやすさ
- システムの全体的なユーザーエクスペリエンス

**テスト方法**：
- テストケースの準備
- ユーザー代表によるテストの実行
- ユーザーフィードバックの収集
- テスト結果の分析

## 6. デプロイ計画設計

### 6.1 デプロイ環境

**ローカルデプロイ**：
- Python 3.8+
- 依存関係：PyYAML、SQLite3、Flask（オプション、REST API 用）

**コンテナデプロイ**：
- Docker イメージ
- Docker Compose 設定

### 6.2 設定管理

**設定ファイル**：
- `config/config.yaml`：システム設定
- `config/rules.yaml`：ルール設定

**環境変数**：
- `MCE_CONFIG_PATH`：設定ファイルのパス
- `MCE_DATA_PATH`：データストレージのパス
- `MCE_LLM_API_KEY`：LLM API キー（オプション）

### 6.3 デプロイ手順

**ローカルデプロイ**：
1. コードリポジトリをクローン
2. 依存関係をインストール：`pip install -r requirements.txt`
3. ルールを設定：`config/rules.yaml` を編集
4. サービスを開始：`python -m memory_classification_engine`

**コンテナデプロイ**：
1. イメージを構築：`docker build -t memory-classification-engine .`
2. コンテナを実行：`docker run -p 5000:5000 memory-classification-engine`

### 6.4 モニタリングとメンテナンス

**モニタリング**：
- ロギング：システムの動作ログ
- パフォーマンスモニタリング：応答時間、リソース使用状況
- エラーモニタリング：例外とエラーの記録

**メンテナンス**：
- 定期的なデータバックアップ
- 定期的なアーカイブメモリーのクリーンアップ
- 定期的なルール設定の更新

## 7. セキュリティ設計

### 7.1 データセキュリティ

- **データ暗号化**：機密メモリー情報の暗号化ストレージ
- **アクセス制御**：ロールベースのアクセス権限管理
- **データ最小化**：必要なメモリー情報のみを保存
- **忘却メカニズム**：ユーザーによるメモリー削除のサポート
- **監査ログ**：すべてのメモリーアクセスと変更操作の記録

### 7.2 API セキュリティ

- **認証**：API アクセスには認証が必要
- **承認**：ロールベースの権限制御
- **入力検証**：注入攻撃を防ぐためのユーザー入力の検証
- **レート制限**：API の濫用を防ぐ
- **HTTPS**：転送データを保護するための HTTPS の使用

## 8. 拡張性設計

### 8.1 モジュール拡張

- **メモリータイプの拡張**：新しいメモリータイプの追加をサポート
- **ストレージバックエンドの拡張**：新しいストレージバックエンドの追加をサポート
- **判断層の拡張**：新しい判断層の追加をサポート

### 8.2 統合拡張

- **エージェントフレームワークの統合**：異なるエージェントフレームワークとの統合をサポート
- **LLM の統合**：異なる LLM との統合をサポート
- **サードパーティサービスの統合**：サードパーティサービスとの統合をサポート

## 9. 技術的リスクと対策

| リスク | 影響 | 対策 |
|------|------|------|
| 意味推論層のパフォーマンス問題 | 応答時間が長すぎて、ユーザーエクスペリエンスに影響 | 軽量モデルを優先、呼び出し頻度を制限、キャッシュメカニズムを実装 |
| ストレージ容量の急速な増加 | システムパフォーマンスの低下、ストレージコストの増加 | 自動忘却メカニズムを実装、低価値メモリーを定期的にクリーンアップ、ストレージ構造を最適化 |
| 複雑なメモリーの競合処理 | システムの動作が予測不可能、ユーザーエクスペリエンスが悪い | 明確な競合解決戦略を設計、ユーザー介入メカニズムを提供、競合履歴を記録 |
| 多言語サポートの難しさ | 言語間のメモリーの一貫性の問題 | 意味に基づくメモリー表現を採用、英語と中国語のサポートを優先、翻訳APIを使用して言語間のマッピングを行う |
| LLM依存のリスク | LLMサービスが利用不可、システム機能が制限される | ダウングレード戦略を実装、LLMが利用不可の場合、ルールマッチングとパターン分析層のみを使用 |

## 10. 改善計画

### 10.1 改善の背景

メモリー分類エンジンはAIエージェントのコアコンポーネントであり、インテリジェントなメモリー分類、階層化ストレージ、効率的な検索、制御可能な忘却を担当しています。AI技術の発展と応用シナリオの拡大に伴い、メモリー分類エンジンは継続的な改善と最適化が必要であり、ますます複雑な要件を満たすために努力しています。現在のシステムにはパフォーマンスの問題があり、パフォーマンスの最適化を優先すると同時に、コードの再構築、設定管理の改善、ドキュメントの強化、依存関係管理の最適化を行う必要があります。

### 10.2 改善の目標

#### 10.2.1 コア目標
- ストレージと検索のパフォーマンスを最適化（主な目標）
- メモリー分類の精度とカバレッジを向上
- システムの拡張性と保守性を強化
- ユーザーエクスペリエンスと統合能力を改善

#### 10.2.2 具体的な目標
- メモリー検索の応答時間を50ms以内に削減
- メモリー分類の精度を90%以上に向上
- システムの起動と実行時間を最適化
- より多くの言語と複雑なシナリオをサポート
- より柔軟な統合インターフェースを提供
- システムの安定性と信頼性を強化
- コードの重複を排除し、コードの再利用性を向上
- ハードコードされたパラメータを設定ファイルに移動
- システムレベルのドキュメントを完成させ、アーキテクチャ設計、APIドキュメントなどを含む
- 仮想環境と依存関係のロックを使用して、バージョンの競合を回避

### 10.3 改善の分野

#### 10.3.1 コアエンジンの改善
- コアエンジンのパフォーマンスと安定性を最適化
- メモリー分類アルゴリズムと戦略を改善
- コンテキスト理解能力を強化
- システムの設定可能性を向上
- コードの重複を排除し、コードの再利用性を向上

#### 10.3.2 ストレージ層の改善
- ストレージ構造とインデックスを最適化
- ストレージバックエンドのパフォーマンスを向上
- データのセキュリティとプライバシー保護を強化
- より多くのストレージバックエンドオプションをサポート

#### 10.3.3 検索と注入の改善
- メモリー検索アルゴリズムを最適化
- メモリー注入の形式と戦略を改善
- 意味理解と関連性ランキングを強化
- より複雑な検索シナリオをサポート

#### 10.3.4 多言語サポート
- 多言語メモリーの一貫性を強化
- 言語間のメモリーマッピングを改善
- より多くの言語のメモリー分類をサポート
- 言語検出と処理を最適化

#### 10.3.5 拡張性と統合
- より柔軟なSDKとAPIを提供
- 異なるエージェントフレームワークとの統合を強化
- より多くのLLMモデルをサポート
- より多くの統合例を提供

#### 10.3.6 設定管理
- ハードコードされたパラメータを設定ファイルに移動
- 統一された設定管理メカニズムを確立
- 環境変数と設定ファイルの混合設定をサポート
- 設定の検証とデフォルト値の管理を提供

#### 10.3.7 ドキュメントの強化
- システムレベルのドキュメントを完成させ、アーキテクチャ設計、APIドキュメントなどを含む
- 様々な要件/設計ドキュメントを全面的に更新
- READMEと英語版ドキュメントを完成させ
- 詳細な使用例とチュートリアルを提供

#### 10.3.8 依存関係管理
- 仮想環境と依存関係のロックを使用
- バージョンの競合を回避
- 依存関係のインストールと管理を最適化
- 依存関係の更新戦略を確立

### 10.4 実装計画

#### 10.4.1 第1段階：パフォーマンス評価と計画（2週間）
- タスク1.1：パフォーマンス評価 - 現在のシステムのパフォーマンスのボトルネックと問題を評価
- タスク1.2：コード分析 - コード構造と重複を分析
- タスク1.3：改善計画 - 詳細な改善計画を策定し、パフォーマンスの最適化を優先
- タスク1.4：技術研究 - 関連するパフォーマンス最適化技術とソリューションを研究

#### 10.4.2 第2段階：コアパフォーマンスの最適化（4週間）
- タスク2.1：ストレージ層のパフォーマンス最適化 - ストレージ構造とインデックスを最適化し、ストレージと検索のパフォーマンスを向上
- タスク2.2：検索アルゴリズムの最適化 - メモリー検索アルゴリズムを最適化し、応答時間を削減
- タスク2.3：コアエンジンのパフォーマンス最適化 - コアエンジンのパフォーマンスと安定性を最適化
- タスク2.4：コードの再構築 - コードの重複を排除し、コードの再利用性を向上
- タスク2.5：設定管理の改善 - ハードコードされたパラメータを設定ファイルに移動し、統一された設定管理メカニズムを確立

#### 10.4.3 第3段階：機能強化と統合（3週間）
- タスク3.1：メモリー分類アルゴリズムの改善 - メモリー分類アルゴリズムと戦略を改善し、精度を向上
- タスク3.2：多言語サポートの強化 - 多言語メモリーの一貫性とサポートを強化
- タスク3.3：SDKとAPIの改善 - より柔軟なSDKとAPIを提供
- タスク3.4：フレームワークとLLMの統合 - 異なるエージェントフレームワークとLLMモデルとの統合を強化

#### 10.4.4 第4段階：ドキュメントの強化と依存関係管理（2週間）
- タスク4.1：ドキュメントの強化 - システムレベルのドキュメントを完成させ、アーキテクチャ設計、APIドキュメントなどを含む；様々な要件/設計ドキュメントを全面的に更新し、READMEと英語版を含む
- タスク4.2：依存関係管理の改善 - 仮想環境と依存関係のロックを使用し、バージョンの競合を回避
- タスク4.3：テストと最適化 - テストを作成し実行し、テスト結果に基づいて最適化と修正を行う

#### 10.4.5 第5段階：デプロイとパフォーマンス検証（1週間）
- タスク5.1：デプロイの準備 - デプロイ環境と設定を準備
- タスク5.2：システムのデプロイ - システムを目標環境にデプロイ
- タスク5.3：パフォーマンス検証 - システムのパフォーマンスが目標を満たしているかどうかを検証
- タスク5.4：モニタリングの設定とトレーニング - システムのモニタリングとアラートを設定し、トレーニングとドキュメントを提供

### 10.5 期待される結果

#### 10.5.1 技術的結果
- 最適化されたメモリー分類エンジン
- 改善されたストレージと検索のパフォーマンス
- 強化された多言語サポート
- より柔軟な統合インターフェース
- 完全なテストとドキュメント

#### 10.5.2 ビジネス結果
- AIエージェントのメモリー能力の向上
- ユーザーエクスペリエンスの強化
- システムリソース使用の削減
- システムの安定性と信頼性の向上
- より多くのアプリケーションシナリオのサポート

### 10.6 成功の指標

- メモリー分類の精度 ≥ 90%
- メモリー検索の応答時間 ≤ 50ms
- システムの安定性 ≥ 99.9%
- ユーザー満足度 ≥ 85%
- 統合成功率 ≥ 95%

## 11. 結論

本詳細設計文書は、メモリー分類エンジンのための完全な技術実装計画を提供しており、システムアーキテクチャ、コアモジュール設計、データモデル設計、APIインターフェース設計、テスト計画設計、デプロイ計画設計、セキュリティ設計、拡張性設計を含んでいます。

この設計は、モジュール式の階層化アーキテクチャを採用しており、システムの拡張性と保守性を確保しています。同時に、軽量な技術選択により、リソースが制限された環境でもシステムが正常に動作することを保証しています。

この設計は、ユーザーの要件と技術的な課題を十分に考慮し、メモリー分類エンジンのための完全で実用的な実装計画を提供しています。

改善計画の実施を通じて、メモリー分類エンジンは継続的に最適化と改善が行われ、AIエージェントによりインテリジェントで効率的なメモリー管理能力を提供し、より複雑なアプリケーションシナリオをサポートします。