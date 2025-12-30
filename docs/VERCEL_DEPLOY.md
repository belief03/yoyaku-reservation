# Vercelデプロイガイド

## 📋 前提条件

1. **Vercelアカウント**を作成
   - https://vercel.com/ で無料アカウント作成

2. **GitHubアカウント**（推奨）
   - コードをGitHubにプッシュするため

3. **環境変数の準備**
   - Supabase設定
   - SMTP設定（Resend等）

## 🚀 デプロイ方法

### ⚠️ 注意: 日本語ユーザー名の場合

Windowsでユーザー名に日本語が含まれている場合、Vercel CLIでエラーが発生する可能性があります。
**GitHub経由のデプロイ（方法2）を推奨します。**

### 方法1: Vercel CLIを使用

> **注意**: ユーザー名に日本語が含まれている場合、エラーが発生する可能性があります。
> その場合は「方法2: GitHubと連携」を使用してください。

#### Step 1: Vercel CLIをインストール

```bash
npm install -g vercel
```

#### Step 2: Vercelにログイン

```bash
vercel login
```

**エラーが発生した場合**: GitHub経由のデプロイ（方法2）を使用してください。

#### Step 3: デプロイ

```bash
vercel
vercel --prod
```

### 方法2: GitHubと連携（自動デプロイ・推奨）

#### Step 1: GitHubにリポジトリを作成

1. **GitHubで新しいリポジトリを作成**
   - https://github.com/new にアクセス
   - リポジトリ名を入力（例: `yoyaku-reservation`）
   - 「Create repository」をクリック

2. **ローカルでGitを初期化（まだの場合）**

```bash
# Gitがインストールされているか確認
git --version

# Gitを初期化
git init

# ファイルを追加
git add .

# コミット
git commit -m "Initial commit"

# ブランチ名をmainに変更
git branch -M main

# GitHubリポジトリを追加（your-usernameを実際のユーザー名に変更）
git remote add origin https://github.com/your-username/yoyaku-reservation.git

# プッシュ
git push -u origin main
```

**注意**: `.env`ファイルは`.gitignore`に含まれているため、GitHubにプッシュされません。
環境変数は後でVercel Dashboardで設定します。

#### Step 2: Vercelでプロジェクトをインポート

1. Vercel Dashboardにアクセス: https://vercel.com/dashboard
2. 「Add New...」→「Project」をクリック
3. 「Import Git Repository」でGitHubリポジトリを選択
4. 「Import」をクリック

#### Step 3: プロジェクト設定

Vercelが自動的にFastAPIプロジェクトを検出します。

- **Framework Preset**: Other
- **Root Directory**: `./`
- **Build Command**: （空欄のまま）
- **Output Directory**: （空欄のまま）

#### Step 4: 環境変数を設定

「Environment Variables」セクションで以下を追加：

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=re_xxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@yourdomain.com
SECRET_KEY=your_secret_key_here
ADMIN_API_KEY=your_admin_api_key
```

#### Step 5: デプロイ

「Deploy」をクリックしてデプロイを開始します。

## ⚙️ 環境変数の設定

Vercel Dashboardで環境変数を設定：

1. プロジェクトを選択
2. 「Settings」→「Environment Variables」
3. 以下の変数を追加：

### 必須設定

```
SUPABASE_URL
SUPABASE_KEY
SUPABASE_SERVICE_KEY
SECRET_KEY
```

### メール設定（Resend使用）

```
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=re_xxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@yourdomain.com
```

### オプション設定

```
ADMIN_API_KEY
BASE_URL=https://your-app.vercel.app
```

## 🔍 デプロイ後の確認

### 1. ヘルスチェック

```
https://your-app.vercel.app/health
```

正常な場合：`{"status":"healthy"}` が返ります

### 2. APIドキュメント

```
https://your-app.vercel.app/docs
```

### 3. ユーザーUI

```
https://your-app.vercel.app/
```

## 🛠️ トラブルシューティング

### エラー: Module not found

`requirements.txt`に必要なパッケージが含まれているか確認：

```bash
pip freeze > requirements.txt
```

### エラー: Environment variable not set

Vercel Dashboardで環境変数が正しく設定されているか確認

### エラー: Static files not found

`static/`ディレクトリが正しく配置されているか確認

## 📝 今後の更新

### GitHub連携の場合

コードをプッシュするだけで自動デプロイ：

```bash
git add .
git commit -m "Update"
git push
```

### CLIの場合

```bash
vercel --prod
```

## 🔗 参考リンク

- [Vercel公式ドキュメント](https://vercel.com/docs)
- [FastAPI on Vercel](https://vercel.com/guides/deploying-fastapi-with-vercel)

