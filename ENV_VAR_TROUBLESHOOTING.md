# 環境変数のトラブルシューティング

## ⚠️ 問題: 環境変数を設定しても動作しない

## 🔍 確認事項

### 1. 環境変数の値が空でないか確認

Vercelダッシュボードで以下を確認してください：

1. 「Settings」→「Environment Variables」を開く
2. 各環境変数をクリックして編集
3. **値が空でないか確認**
4. **値の前後に余分なスペースがないか確認**

### 2. 環境変数のキー名が正しいか確認

**正しいキー名（大文字小文字を正確に）:**
- `SUPABASE_URL` （❌ `supabase_url` ではない）
- `SUPABASE_KEY` （❌ `supabase_key` ではない）
- `SUPABASE_SERVICE_KEY` （❌ `supabase_service_key` ではない）
- `SECRET_KEY` （❌ `secret_key` ではない）

### 3. 環境変数の値の形式を確認

#### SUPABASE_URL
- ✅ 正しい形式: `https://xxxxx.supabase.co`
- ❌ 間違い: `https://xxxxx.supabase.co/` （末尾のスラッシュ不要）
- ❌ 間違い: 値が空

#### SUPABASE_KEY
- ✅ 正しい形式: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` （長い文字列）
- ❌ 間違い: 値が空
- ❌ 間違い: URLを設定している

#### SUPABASE_SERVICE_KEY
- ✅ 正しい形式: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` （長い文字列）
- ❌ 間違い: 値が空
- ❌ 間違い: SUPABASE_KEYと同じ値を設定している

#### SECRET_KEY
- ✅ 正しい形式: ランダムな文字列（例: `Q_IqN5oPm_osND4HO9Jjsk6zWq4VgfwXgaK6vzEVdGo`）
- ❌ 間違い: 値が空
- ❌ 間違い: `your-secret-key-here-change-in-production` のまま（本番環境では変更が必要）

### 4. 環境変数の設定手順（再確認）

1. Vercelダッシュボードでプロジェクトを開く
2. 「Settings」→「Environment Variables」を開く
3. **「Add New」** をクリック
4. **キー名を正確に入力**（大文字小文字を正確に）
5. **値を入力**（コピー&ペーストで確実に）
6. **環境を選択**: 
   - ✅ **Production（制作）** にチェック
   - ✅ **Preview（プレビュー）** にもチェック（推奨）
7. **「Save」をクリック**
8. **必ず再デプロイを実行**

### 5. 環境変数の削除と再設定

もし環境変数が正しく動作しない場合：

1. **既存の環境変数を削除**
   - 各環境変数の右側の「...」メニューから「Delete」を選択
2. **再度追加**
   - 上記の手順に従って、正しいキー名と値で追加
3. **再デプロイ**
   - 「展開」（Deployments）タブから再デプロイを実行

## 🔍 診断方法

### 方法1: `/health` エンドポイントで確認

デプロイ後、以下のURLにアクセス：
```
https://yoyaku-booking-system.vercel.app/health
```

エラーの場合、以下のような情報が表示されます：
```json
{
  "status": "error",
  "message": "...",
  "missing_env_vars": ["SUPABASE_URL", "SUPABASE_KEY"],
  "env_status": {
    "SUPABASE_URL": {
      "set": false,
      "length": 0,
      "preview": null
    }
  }
}
```

### 方法2: Vercelのログで確認

1. Vercelダッシュボードで「ログ」（Logs）タブを開く
2. 以下のようなメッセージを確認：
   - `[ENV] SUPABASE_URL is set (length: 45)` → 正常
   - `[ERROR] Missing environment variables: SUPABASE_URL, SUPABASE_KEY` → 環境変数が設定されていない

## 📋 チェックリスト

- [ ] 環境変数のキー名が正確か（大文字小文字）
- [ ] 環境変数の値が空でないか
- [ ] 値の前後に余分なスペースがないか
- [ ] Production環境に設定されているか
- [ ] 環境変数設定後に再デプロイを実行したか
- [ ] `/health` エンドポイントで環境変数の状態を確認したか
- [ ] Vercelのログでエラーメッセージを確認したか

## 🚨 よくある間違い

### 間違い1: キー名の大文字小文字
```
❌ 間違い: supabase_url
✅ 正しい: SUPABASE_URL
```

### 間違い2: 値が空
```
❌ 間違い: キー: SUPABASE_URL, 値: （空）
✅ 正しい: キー: SUPABASE_URL, 値: https://xxxxx.supabase.co
```

### 間違い3: 環境変数設定後に再デプロイしていない
```
❌ 間違い: 環境変数を設定したが、再デプロイしていない
✅ 正しい: 環境変数を設定した後、必ず再デプロイを実行
```

### 間違い4: プレビュー環境のみに設定している
```
❌ 間違い: Preview環境のみに設定
✅ 正しい: Production環境にも設定（必須）
```

## 💡 解決方法

1. **環境変数を一度すべて削除**
2. **正しいキー名と値で再設定**
3. **Production環境に設定**
4. **再デプロイを実行**
5. **`/health` エンドポイントで確認**

