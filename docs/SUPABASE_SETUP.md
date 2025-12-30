# Supabase設定ガイド

このドキュメントでは、予約管理システムのSupabase設定手順を説明します。

## 📋 目次

1. [Supabaseプロジェクトの作成](#1-supabaseプロジェクトの作成)
2. [認証情報の取得](#2-認証情報の取得)
3. [データベーススキーマの作成](#3-データベーススキーマの作成)
4. [ストレージバケットの設定](#4-ストレージバケットの設定)
5. [環境変数の設定](#5-環境変数の設定)
6. [動作確認](#6-動作確認)

---

## 1. Supabaseプロジェクトの作成

### 1.1 Supabaseアカウントの作成

1. [Supabase公式サイト](https://supabase.com/)にアクセス
2. 「Start your project」をクリック
3. GitHubアカウントでサインアップ（推奨）またはメールアドレスで登録

### 1.2 新しいプロジェクトの作成

1. ダッシュボードで「New Project」をクリック
2. 以下の情報を入力：
   - **Organization**: 既存の組織を選択、または新規作成
   - **Name**: `yoyaku-reservation-system`（任意の名前）
   - **Database Password**: 強力なパスワードを設定（**必ず保存してください**）
   - **Region**: 最寄りのリージョンを選択（例: `Tokyo (ap-northeast-1)`）
   - **Pricing Plan**: Free tierで開始可能

3. 「Create new project」をクリック
4. プロジェクトの作成完了まで2-3分待機

---

## 2. 認証情報の取得

### 2.1 API認証情報の取得

1. プロジェクトダッシュボードに移動
2. 左サイドバーの「Settings」→「API」をクリック
3. 以下の情報をコピー：

   ```
   Project URL: https://xxxxxxxxxxxxx.supabase.co
   anon/public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

   ⚠️ **重要**: `service_role key`は管理者権限を持つため、**絶対に公開しないでください**

### 2.2 データベース接続情報の取得（オプション）

1. 「Settings」→「Database」をクリック
2. 「Connection string」セクションで接続文字列を確認
3. 必要に応じてコピー（通常はAPIキーで十分）

---

## 3. データベーススキーマの作成

### 3.1 SQL Editorを開く

1. 左サイドバーの「SQL Editor」をクリック
2. 「New query」をクリック

### 3.2 スキーマの実行

1. `database/schema.sql`ファイルの内容をコピー
2. SQL Editorに貼り付け
3. 「Run」ボタンをクリック（または `Ctrl+Enter`）
4. エラーがないことを確認

### 3.3 初期データの投入（オプション）

1. `database/seed.sql`ファイルの内容を実行（テストデータが必要な場合）

---

## 4. ストレージバケットの設定

### 4.1 ストレージバケットの作成

1. 左サイドバーの「Storage」をクリック
2. 「New bucket」をクリック
3. 以下の設定で作成：
   - **Name**: `uploads`
   - **Public bucket**: ✅ チェック（画像などを公開する場合）
   - **File size limit**: `10MB`（または必要に応じて）
   - **Allowed MIME types**: 空欄（すべて許可）または特定のタイプを指定

4. 「Create bucket」をクリック

### 4.2 ストレージポリシーの設定（オプション）

セキュリティのため、必要に応じてRow Level Security (RLS) ポリシーを設定します。

---

## 5. 環境変数の設定

### 5.1 .envファイルの作成

プロジェクトルートに`.env`ファイルを作成します。

### 5.2 認証情報の設定

`.env`ファイルに以下を記述：

```env
# Supabase設定（必須）
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# ファイルストレージ設定
STORAGE_BUCKET=uploads

# セキュリティ設定（本番環境では必ず変更）
SECRET_KEY=your-secret-key-here-change-in-production

# メール設定（オプション、後で設定可能）
# SMTP_HOST=smtp.example.com
# SMTP_PORT=587
# SMTP_USER=your_email@example.com
# SMTP_PASSWORD=your_password
# EMAIL_FROM=noreply@example.com

# AI設定（オプション）
# OPENAI_API_KEY=your_openai_api_key
# AI_ENABLED=false
```

### 5.3 ファイルの保護

`.env`ファイルは`.gitignore`に含まれているため、Gitにコミットされません。

---

## 6. 動作確認

### 6.1 接続テスト

1. ターミナルでプロジェクトディレクトリに移動
2. 依存関係をインストール：
   ```bash
   pip install -r requirements.txt
   ```

3. Pythonで接続テストを実行：
   ```bash
   python scripts/test_connection.py
   ```

### 6.2 APIサーバーの起動

```bash
uvicorn api.main:app --reload
```

### 6.3 ヘルスチェック

ブラウザまたはcurlで以下にアクセス：

```bash
curl http://localhost:8000/health
```

正常な場合、以下のレスポンスが返ります：

```json
{"status": "healthy"}
```

### 6.4 APIドキュメントの確認

ブラウザで以下にアクセス：

```
http://localhost:8000/docs
```

Swagger UIが表示され、すべてのAPIエンドポイントが確認できます。

---

## 🔒 セキュリティのベストプラクティス

1. **APIキーの管理**
   - `SUPABASE_SERVICE_KEY`は絶対に公開しない
   - `.env`ファイルをGitにコミットしない
   - 本番環境では環境変数を使用

2. **Row Level Security (RLS)**
   - 本番環境ではRLSポリシーを設定することを推奨
   - 各テーブルに適切なアクセス制御を設定

3. **データベースパスワード**
   - 強力なパスワードを使用
   - パスワードマネージャーで安全に保管

---

## 🐛 トラブルシューティング

### 接続エラーが発生する場合

1. `.env`ファイルの値が正しいか確認
2. Supabaseプロジェクトがアクティブか確認
3. ネットワーク接続を確認

### テーブルが見つからないエラー

1. SQLスキーマが正しく実行されたか確認
2. Supabaseダッシュボードでテーブル一覧を確認
3. 必要に応じてスキーマを再実行

### ストレージエラー

1. バケットが作成されているか確認
2. バケット名が`.env`の`STORAGE_BUCKET`と一致しているか確認
3. バケットの公開設定を確認

---

## 📚 参考リンク

- [Supabase公式ドキュメント](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase/supabase-py)
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)

---

## ✅ チェックリスト

設定が完了したら、以下を確認してください：

- [ ] Supabaseプロジェクトが作成された
- [ ] API認証情報（URL、anon key、service_role key）を取得した
- [ ] データベーススキーマが実行された
- [ ] ストレージバケットが作成された
- [ ] `.env`ファイルが作成され、認証情報が設定された
- [ ] 接続テストが成功した
- [ ] APIサーバーが起動した
- [ ] ヘルスチェックが成功した

すべてチェックが付いたら、設定完了です！🎉






