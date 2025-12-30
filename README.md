# Yoyaku Reservation System

予約管理システムのAPIサーバー

> **👋 はじめに**: 美容院経営者の方は [取説（美容院経営者向け）](docs/取説_美容院経営者向け.md) をまずお読みください。  
> 開発者の方は [システム起動ガイド](docs/STARTUP_GUIDE.md) を参照してください。

## 機能

- **予約管理**: 予約の作成、更新、キャンセル、確認
- **顧客管理**: 顧客情報の管理と履歴追跡
- **スタイリスト管理**: スタイリスト情報とスケジュール管理
- **サービス管理**: 提供サービスの管理
- **商品管理**: 商品と在庫管理
- **注文管理**: 注文処理と支払い管理
- **クーポン管理**: クーポンの作成と検証
- **キャンペーン管理**: マーケティングキャンペーンの管理
- **ファイルストレージ**: 画像やファイルのアップロード管理
- **AIレコメンデーション**: 顧客へのサービス・商品推薦
- **マーケティング**: キャンペーンの自動実行と管理

## セットアップ

### クイックスタート

1. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
   ```

2. **Supabaseの設定**
   - 📖 詳細な手順は [`docs/SUPABASE_SETUP.md`](docs/SUPABASE_SETUP.md) を参照してください
   - ✅ チェックリストは [`docs/SETUP_CHECKLIST.md`](docs/SETUP_CHECKLIST.md) を参照してください

3. **環境変数の設定**

`.env`ファイルを作成し、以下の変数を設定してください：

```env
# Supabase設定
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# データベース設定（オプション）
DATABASE_URL=your_database_url

# セキュリティ設定
SECRET_KEY=your_secret_key_here

# ファイルストレージ設定
STORAGE_BUCKET=uploads

# メール設定（オプション）
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_password
EMAIL_FROM=noreply@example.com

# AI設定（オプション）
OPENAI_API_KEY=your_openai_api_key
AI_ENABLED=false
```

4. **接続テスト**

```bash
python scripts/test_connection.py
```

5. **サーバーの起動**

```bash
python -m api.main
```

または

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### セットアップの詳細

- **Supabase設定ガイド**: [`docs/SUPABASE_SETUP.md`](docs/SUPABASE_SETUP.md)
- **セットアップチェックリスト**: [`docs/SETUP_CHECKLIST.md`](docs/SETUP_CHECKLIST.md)
- **データベーススキーマ**: [`database/schema.sql`](database/schema.sql)
- **テストデータ**: [`database/seed.sql`](database/seed.sql)

## APIエンドポイント

### 予約管理 (`/api/v1/reservations`)
- `POST /` - 予約を作成
- `GET /` - 予約一覧を取得
- `GET /{reservation_id}` - 予約詳細を取得
- `PATCH /{reservation_id}` - 予約を更新
- `POST /{reservation_id}/confirm` - 予約を確認
- `POST /{reservation_id}/cancel` - 予約をキャンセル
- `GET /availability/slots` - 利用可能な時間枠を取得

### 顧客管理 (`/api/v1/customers`)
- `POST /` - 顧客を作成
- `GET /` - 顧客一覧を取得
- `GET /{customer_id}` - 顧客詳細を取得
- `PATCH /{customer_id}` - 顧客情報を更新
- `GET /{customer_id}/reservations` - 顧客の予約履歴を取得
- `GET /{customer_id}/orders` - 顧客の注文履歴を取得

### スタイリスト管理 (`/api/v1/stylists`)
- `POST /` - スタイリストを作成
- `GET /` - スタイリスト一覧を取得
- `GET /{stylist_id}` - スタイリスト詳細を取得
- `PATCH /{stylist_id}` - スタイリスト情報を更新
- `GET /{stylist_id}/reservations` - スタイリストの予約一覧を取得

### サービス管理 (`/api/v1/services`)
- `POST /` - サービスを作成
- `GET /` - サービス一覧を取得
- `GET /{service_id}` - サービス詳細を取得
- `PATCH /{service_id}` - サービス情報を更新
- `GET /categories/list` - サービスカテゴリ一覧を取得

### 商品管理 (`/api/v1/products`)
- `POST /` - 商品を作成
- `GET /` - 商品一覧を取得
- `GET /{product_id}` - 商品詳細を取得
- `PATCH /{product_id}` - 商品情報を更新
- `POST /{product_id}/stock` - 在庫を更新
- `GET /categories/list` - 商品カテゴリ一覧を取得

### 注文管理 (`/api/v1/orders`)
- `POST /` - 注文を作成
- `GET /` - 注文一覧を取得
- `GET /{order_id}` - 注文詳細を取得
- `PATCH /{order_id}` - 注文を更新
- `POST /{order_id}/pay` - 支払いを処理
- `POST /{order_id}/cancel` - 注文をキャンセル

### クーポン管理 (`/api/v1/coupons`)
- `POST /` - クーポンを作成
- `GET /` - クーポン一覧を取得
- `GET /{coupon_id}` - クーポン詳細を取得
- `PATCH /{coupon_id}` - クーポン情報を更新
- `POST /validate` - クーポンの有効性を検証
- `GET /code/{code}` - クーポンコードでクーポンを取得

### キャンペーン管理 (`/api/v1/campaigns`)
- `POST /` - キャンペーンを作成
- `GET /` - キャンペーン一覧を取得
- `GET /active` - アクティブなキャンペーン一覧を取得
- `GET /{campaign_id}` - キャンペーン詳細を取得
- `PATCH /{campaign_id}` - キャンペーン情報を更新
- `POST /{campaign_id}/activate` - キャンペーンを有効化
- `POST /{campaign_id}/pause` - キャンペーンを一時停止
- `POST /{campaign_id}/end` - キャンペーンを終了

### ファイルストレージ (`/api/v1/storage`)
- `POST /upload` - ファイルをアップロード
- `GET /list` - ファイル一覧を取得
- `DELETE /{file_path}` - ファイルを削除
- `GET /{file_path}/url` - ファイルの公開URLを取得

## データベース構造

このシステムはSupabaseを使用しています。以下のテーブルが必要です：

- `customers` - 顧客情報
- `stylists` - スタイリスト情報
- `services` - サービス情報
- `products` - 商品情報
- `reservations` - 予約情報
- `orders` - 注文情報
- `coupons` - クーポン情報
- `coupon_usages` - クーポン使用履歴
- `campaigns` - キャンペーン情報

## 開発

### コード構造

```
yoyaku/
├── api/
│   ├── routes/          # APIルート
│   ├── main.py          # FastAPIアプリケーション
│   ├── database.py      # データベース接続
│   ├── models.py        # データモデル
│   ├── schemas.py       # リクエスト/レスポンススキーマ
│   └── supabase_client.py  # Supabaseクライアント
├── marketing/
│   └── campaign_manager.py  # キャンペーンマネージャー
├── ai/
│   └── recommendation_engine.py  # レコメンデーションエンジン
├── config.py            # 設定ファイル
└── requirements.txt     # 依存関係
```

## ライセンス

MIT License


