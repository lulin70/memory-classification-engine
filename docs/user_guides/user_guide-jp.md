# メモリ分類エンジンユーザーガイド

## 1. はじめに

メモリ分類エンジン（Memory Classification Engine）は、ユーザーのメモリを自動的に分類、保存、検索するためのインテリジェントなメモリ管理システムです。このガイドでは、メモリ分類エンジンの様々な機能をどのように使用するかを理解し、その能力を最大限に活用する方法を説明します。

## 2. 基本的な使用方法

### 2.1 エンジンの初期化

```python
from memory_classification_engine import MemoryClassificationEngine

# エンジンを初期化する
engine = MemoryClassificationEngine()
```

### 2.2 メッセージの処理

```python
# ユーザーメッセージを処理する
user_message = "覚えておいて、コードでダッシュを使うのは嫌いだよ"
result = engine.process_message(user_message)
print(result)
# 出力: {"matched": true, "memory_type": "user_preference", "tier": 2, "content": "コードでダッシュを使うのは嫌い", "confidence": 1.0, "source": "rule:0"}
```

### 2.3 メモリの検索

```python
# メモリを検索する
memories = engine.retrieve_memories("コードスタイル")
print(memories)
```

### 2.4 フィードバックの処理

```python
# ユーザーフィードバックを処理する
memory_id = "your_memory_id"
feedback = {"type": "positive", "comment": "This memory is accurate"}
result = engine.process_feedback(memory_id, feedback)
print(result)
```

### 2.5 システムの最適化

```python
# システムを最適化する
result = engine.optimize_system()
print(result)
```

### 2.6 メモリの圧縮

```python
# メモリを圧縮する
tenant_id = "your_tenant_id"
result = engine.compress_memories(tenant_id)
print(result)
```

## 3. Agentフレームワークの使用

### 3.1 Agentの登録

```python
# Agentを登録する
agent_config = {
    'adapter': 'claude_code',  # サポートされているアダプター: claude_code, work_buddy, trae, openclaw
    'api_key': 'your_api_key'  # APIキーが必要な場合
}
result = engine.register_agent('my_agent', agent_config)
print(result)
```

### 3.2 Agentの一覧表示

```python
# 登録されたすべてのAgentを一覧表示する
result = engine.list_agents()
print("登録されたAgent:", result)
```

### 3.3 Agentを使用したメッセージの処理

```python
# Agentを使用してメッセージを処理する
result = engine.process_message_with_agent('my_agent', "Hello, world!")
print("Agent処理結果:", result)
```

### 3.4 Agentの登録解除

```python
# Agentの登録を解除する
result = engine.unregister_agent('my_agent')
print(result)
```

## 4. 知識ベースの統合

### 4.1 メモリを知識ベースに書き戻す

```python
# メモリを知識ベースに書き戻す
memory_id = "your_memory_id"
result = engine.write_memory_to_knowledge(memory_id)
print("知識ベースへの書き戻し結果:", result)
```

### 4.2 知識ベースから知識を取得する

```python
# 知識ベースから関連する知識を取得する
result = engine.get_knowledge("SF小説")
print("知識ベース検索結果:", result)
```

### 4.3 知識ベースの同期

```python
# 知識ベースを同期する
result = engine.sync_knowledge_base()
print("知識ベース同期結果:", result)
```

### 4.4 知識ベースの統計情報を取得する

```python
# 知識ベースの統計情報を取得する
result = engine.get_knowledge_statistics()
print("知識ベース統計情報:", result)
```

## 5. 高度な機能

### 5.1 VS Code 拡張機能

#### 5.1.1 インストールと設定

1. **拡張機能のインストール**：
   - VS Code または Cursor を開く
   - 拡張機能アイコン（左サイドバー）をクリック
   - "Memory Classification Engine" を検索
   - "インストール" をクリック

2. **拡張機能の設定**：
   - VS Code 設定を開く（File → Preferences → Settings）
   - "Memory Classification Engine" を検索
   - MCP サーバーアドレスを設定する（デフォルトは http://localhost:8000）

#### 5.1.2 拡張機能の使用

1. **メモリの表示**：
   - 左サイドバーの "Memory Classification Engine" アイコンをクリック
   - 異なるメモリタイプを展開してメモリを表示

2. **メモリ操作**：
   - メモリを右クリックして "Recall" を選択して詳細を表示
   - メモリを右クリックして "Forget" を選択して削除
   - 上部の "Export" ボタンをクリックしてメモリをエクスポート
   - 上部の "Import" ボタンをクリックしてメモリをインポート

### 5.2 メモリ品質ダッシュボード

#### 5.2.1 ダッシュボードへのアクセス

1. **サーバーの起動**：
   ```bash
   cd memory-classification-engine
   python3 -m memory_classification_engine.api.server
   ```

2. **ダッシュボードへのアクセス**：
   - ブラウザを開き、http://localhost:8000/dashboard/ にアクセス
   - メモリ品質の統計とグラフを表示

#### 5.2.2 ダッシュボードの使用

1. **時間範囲のフィルタリング**：
   - 異なる時間範囲を選択する（7日、30日、90日）
   - "Refresh" ボタンをクリックしてデータを更新

2. **詳細情報の表示**：
   - メモリ品質のトレンドグラフを表示
   - メモリタイプの分布を表示
   - メモリ品質の詳細テーブルを表示

### 5.3 確認待ちメモリ

#### 5.3.1 確認待ちメモリの追加

```python
# 確認待ちメモリを追加する
memory = {
    'memory_type': 'user_preference',
    'content': 'I prefer using Python',
    'confidence': 0.95
}
memory_id = engine.add_pending_memory(memory)
print(f"Pending memory ID: {memory_id}")
```

#### 5.3.2 確認待ちメモリの処理

```python
# 確認待ちメモリを取得する
pending_memories = engine.get_pending_memories()
print(f"Pending memories: {len(pending_memories)}")

# メモリを承認する
if pending_memories:
    memory_id = pending_memories[0]['id']
    success = engine.approve_memory(memory_id)
    print(f"Approved memory: {success}")

# メモリを拒否する
if pending_memories:
    memory_id = pending_memories[0]['id']
    success = engine.reject_memory(memory_id)
    print(f"Rejected memory: {success}")

# 確認待ちメモリの数を取得する
count = engine.get_pending_count()
print(f"Pending memories count: {count}")
```

### 5.4 Nudge メカニズム

#### 5.4.1 Nudge 候補の取得

```python
# Nudge 候補を取得する
nudge_candidates = engine.get_nudge_candidates(limit=5)
print(f"Nudge candidates: {len(nudge_candidates)}")

# Nudge プロンプトを生成する
if nudge_candidates:
    prompt = engine.generate_nudge_prompt(nudge_candidates[0])
    print("Nudge prompt:")
    print(prompt)
```

#### 5.4.2 Nudge インタラクションの記録

```python
# Nudge インタラクションを記録する
if nudge_candidates:
    memory_id = nudge_candidates[0]['id']
    success = engine.record_nudge_interaction(memory_id, 'confirm')
    print(f"Recorded nudge interaction: {success}")

# Nudge するかどうかをチェックする
should_nudge = engine.should_nudge()
print(f"Should nudge: {should_nudge}")
```

### 5.5 マルチテナント管理

```python
# テナントを作成する
tenant_id = "company_tenant"
result = engine.tenant_manager.create_tenant(
    tenant_id,
    "Company Tenant",
    "enterprise",
    user_id="admin"
)
print("テナント作成結果:", result)

# テナントを取得する
tenant = engine.tenant_manager.get_tenant(tenant_id)
print("テナント情報:", tenant)

# すべてのテナントを一覧表示する
tenants = engine.tenant_manager.list_tenants()
print("すべてのテナント:", tenants)
```

### 5.6 プライバシー設定

```python
# ユーザーのプライバシー設定を設定する
user_id = "user1"
settings = {
    "data_retention_days": 30,
    "enable_encryption": True,
    "share_with_agents": False
}
result = engine.privacy_manager.set_user_settings(user_id, settings)
print("プライバシー設定の設定結果:", result)

# ユーザーのプライバシー設定を取得する
result = engine.privacy_manager.get_user_settings(user_id)
print("ユーザーのプライバシー設定:", result)

# ユーザーデータをエクスポートする
result = engine.privacy_manager.export_user_data(user_id)
print("ユーザーデータのエクスポート結果:", result)

# ユーザーデータを削除する
result = engine.privacy_manager.delete_user_data(user_id)
print("ユーザーデータの削除結果:", result)
```

### 5.7 監査ログ

```python
# 監査ログを表示する
logs = engine.audit_manager.get_logs(user_id="user1", action="process_message")
print("監査ログ:", logs)

# 監査レポートを生成する
report = engine.audit_manager.generate_report(start_time="2026-01-01", end_time="2026-01-31")
print("監査レポート:", report)
```

### 5.8 パフォーマンス監視

```python
# パフォーマンスメトリクスを取得する
metrics = engine.performance_monitor.get_metrics()
print("パフォーマンスメトリクス:", metrics)

# パフォーマンスメトリクスをリセットする
engine.performance_monitor.reset_metrics()
print("パフォーマンスメトリクスをリセットしました")
```

## 6. ベストプラクティス

### 6.1 メモリ管理

- **定期的な最適化**：システムパフォーマンスを最適化するために、定期的に `optimize_system()` メソッドを呼び出してください。毎日または毎週実行することを推奨します。
- **メモリの圧縮**：メモリを圧縮してストレージスペースを削減するために、定期的に `compress_memories()` メソッドを呼び出してください。毎月実行することを推奨します。
- **重要度の設定**：重要なメモリについては、高い重要度レベルを設定して、それらが忘れられないようにしてください。
- **バッチ操作**：大量のメモリ操作については、効率を上げるために個々の操作ではなくバッチAPIを使用してください。
- **メモリタグ**：メモリにタグを追加して、後での検索と管理を容易にしてください。

### 6.2 Agentの使用

- **適切なAgentの選択**：タスクの種類に応じて適切なAgentフレームワークを選択してください。例えば、コード生成にはClaudeCode、協力的なタスクにはWorkBuddyが適しています。
- **Agentのライフサイクル管理**：Agentを使用し終えた後は、リソースを解放するためにすぐに登録を解除してください。
- **Agentパラメータの設定**：最適な結果を得るために、具体的な要件に基づいてAgentのパラメータを設定してください。
- **Agentの組み合わせ**：複雑なタスクについては、複数のAgentの能力を組み合わせることができます。
- **エラー処理**：システムの安定性を向上させるために、Agent操作に適切なエラー処理を追加してください。

### 6.3 知識ベースの統合

- **Obsidian vaultの設定**：メモリが知識ベースに正しく書き戻されるように、Obsidian vaultのパスを正しく設定してください。
- **定期的な同期**：データの一貫性を確保するために、定期的に `sync_knowledge_base()` メソッドを呼び出して知識ベースを同期してください。
- **知識の適切な整理**：Obsidianでは、フォルダとタグを使用して知識を適切に整理してください。
- **知識のリンク**：Obsidianで知識間のリンクを作成して、知識ネットワークを形成してください。
- **バージョン管理**：Obsidian vaultを管理するために、Gitなどのバージョン管理システムの使用を検討してください。

### 6.4 パフォーマンスの最適化

- **キャッシュサイズの調整**：パフォーマンスとメモリ使用量のバランスをとるために、システムリソースに基づいてキャッシュサイズを調整してください。
- **不要な機能の無効化**：特定の機能（LLMやNeo4jなど）が必要でない場合は、設定ファイルでそれらを無効にしてパフォーマンスを向上させてください。
- **ストレージの最適化**：ストレージの負荷を軽減するために、不要なメモリを定期的にクリーンアップしてください。
- **バッチ処理**：大量のデータ操作については、データベースアクセス回数を減らすためにバッチ処理を使用してください。
- **非同期操作**：時間のかかる操作については、システムの応答速度を向上させるために非同期処理の使用を検討してください。
- **ハードウェアの最適化**：システム負荷に応じて、メモリを適切に増やすかSSDストレージを使用してください。

### 6.5 セキュリティのベストプラクティス

- **APIキーの管理**：APIキーをハードコーディングしないでください。環境変数またはキー管理サービスを使用してAPIキーを保存してください。
- **データ暗号化**：ユーザープライバシーを保護するために、機密データの暗号化を有効にしてください。
- **アクセス制御**：メモリへのアクセスを制限するために、適切なアクセス権限を設定してください。
- **監査ログ**：システム操作を記録するために、監査ログを有効にしてください。
- **定期的なバックアップ**：データ損失を防ぐために、メモリデータの定期的なバックアップを行ってください。

### 6.6 一般的な使用シナリオ

#### 6.6.1 インテリジェントカスタマーサービス

```python
# エンジンを初期化する
engine = MemoryClassificationEngine()

# 顧客の問い合わせを処理する
def handle_customer_query(user_id, query):
    # 関連するメモリを検索する
    memories = engine.retrieve_memories(query, user_id=user_id)
    
    # コンテキストを構築する
    context = {
        "user_id": user_id,
        "previous_memories": memories
    }
    
    # 問い合わせを処理する
    result = engine.process_message(query, context=context)
    
    # 新しいメモリを保存する
    if result.get("matches"):
        for match in result["matches"]:
            # 追加のメタデータを追加することができます
            match["user_id"] = user_id
            engine.manage_memory("edit", match["id"], match)
    
    return result
```

#### 6.6.2 パーソナルアシスタント

```python
# エンジンを初期化する
engine = MemoryClassificationEngine()

# ユーザーの好みを管理する
def update_user_preference(user_id, preference):
    result = engine.process_message(
        f"ユーザーの好み：{preference}",
        context={"user_id": user_id, "memory_type": "user_preference"}
    )
    return result

# ユーザーの好みを検索する
def get_user_preferences(user_id):
    memories = engine.retrieve_memories(
        "user_preference",
        memory_type="user_preference",
        user_id=user_id
    )
    return memories

# インテリジェントな推奨

def recommend_content(user_id, current_topic):
    # 関連するメモリを検索する
    memories = engine.retrieve_memories(
        current_topic,
        user_id=user_id,
        limit=5
    )
    
    # メモリに基づいて推奨を生成する
    recommendations = []
    for memory in memories:
        if "preference" in memory.get("content", "").lower():
            recommendations.append(memory["content"])
    
    return recommendations
```

#### 6.6.3 エンタープライズ知識管理

```python
# エンジンを初期化する
engine = MemoryClassificationEngine()

# 企業テナントを作成する
def create_company_tenant(company_id, company_name):
    result = engine.tenant_manager.create_tenant(
        company_id,
        company_name,
        "enterprise"
    )
    return result

# メモリをチームと共有する
def share_memory_to_team(memory_id, team_id):
    result = engine.manage_memory(
        "edit",
        memory_id,
        {"visibility": "team", "team_id": team_id}
    )
    return result

# 企業の知識を一括インポートする
def import_company_knowledge(company_id, knowledge_items):
    for item in knowledge_items:
        result = engine.process_message(
            item["content"],
            context={
                "user_id": "system",
                "tenant_id": company_id,
                "memory_type": "fact_declaration"
            }
        )
    return len(knowledge_items)
```

## 7. トラブルシューティング

### 7.1 よくある問題

#### 7.1.1 メモリ分類の精度が低い

**問題**：メモリ分類の結果が期待どおりでない。

**解決策**：
- ルールの設定が正しいか確認してください
- 分類の精度を向上させるためにLLM機能を有効にすることを検討してください
- システムが学習し改善するのを助けるためにフィードバックを提供してください

#### 7.1.2 パフォーマンスの問題

**問題**：システムの応答が遅いかメモリ使用量が高すぎる。

**解決策**：
- キャッシュサイズとバッチ処理サイズを調整してください
- 不要な機能を無効にしてください
- 定期的にシステムを最適化し、メモリを圧縮してください

#### 7.1.3 知識ベースの統合の問題

**問題**：メモリを知識ベースに書き戻すことができないか、知識ベースから知識を取得することができない。

**解決策**：
- Obsidianがインストールされていること、およびvaultのパスが正しく設定されていることを確認してください
- ファイル権限を確認してください
- Obsidian vaultディレクトリが存在することを確認してください

#### 7.1.4 Agentフレームワークの問題

**問題**：Agentを登録または使用することができない。

**解決策**：
- Agentアダプターが正しくインストールされているか確認してください
- APIキーが有効であることを確認してください（必要な場合）
- ネットワーク接続を確認してください

### 7.2 ログとデバッグ

- **ログの表示**：システムは、システムの状態とエラー情報を理解するのに役立つ詳細なログを生成します
- **デバッグモードの有効化**：より詳細なデバッグ情報を取得するには、設定ファイルで `debug: true` を設定してください
- **パフォーマンス監視の使用**：潜在的な問題を特定するために、定期的にパフォーマンスメトリクスをチェックしてください

### 7.3 サポートのお問い合わせ

解決できない問題が発生した場合は、GitHubリポジトリでissueを作成し、詳細なエラー情報と再現手順を提供してください。できるだけ早く問題を解決するお手伝いをします。

## 8. まとめ

メモリ分類エンジンは、強力なインテリジェントメモリ管理システムです。その様々な機能を適切に使用することで、以下のことができます：

- ユーザーのメモリを自動的に分類して保存する
- 関連するメモリをインテリジェントに検索する
- 様々なAgentフレームワークと統合してシステムの機能を拡張する
- Obsidianなどの知識ベースツールと統合して、知識の双方向フローを実現する
- ユーザーのプライバシーを保護し、データセキュリティを確保する
- システムパフォーマンスを最適化し、応答速度を向上させる

このガイドが、メモリ分類エンジンの能力を最大限に活用して、アプリケーションやサービスにインテリジェントなメモリ管理機能を追加するのに役立つことを願っています。