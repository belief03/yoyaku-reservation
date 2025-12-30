# アクセスURL一覧

## 🌐 ポート8000で利用可能なすべてのURL

### 1. **ユーザーUI画面**
```
http://localhost:8000/
```
または
```
http://localhost:8000/static/index.html
```
- 予約システムのメインUI
- サービス一覧、予約作成、商品一覧、注文、クーポン、キャンペーン、おすすめ機能など

### 2. **APIドキュメント（Swagger UI）**
```
http://localhost:8000/docs
```
- インタラクティブなAPIドキュメント
- すべてのAPIエンドポイントを確認・テスト可能
- 「Try it out」で実際にAPIを実行できます

### 3. **APIドキュメント（ReDoc）**
```
http://localhost:8000/redoc
```
- ReDoc形式のAPIドキュメント
- より読みやすい形式でAPI仕様を確認

### 4. **ヘルスチェック**
```
http://localhost:8000/health
```
- サーバーの稼働状況を確認

### 5. **招待リンクページ**
```
http://localhost:8000/invite/{token}
```
- 店舗アカウント設定ページ
- 招待トークンを使用してアクセス
- 例: `http://localhost:8000/invite/xxxxxxxxxxxxx`

### 6. **管理画面**
```
http://localhost:8000/admin
```
または
```
http://localhost:8000/static/admin.html
```
- 店舗管理画面
- ログインが必要

### 7. **APIルート**
```
http://localhost:8000/
```
- プロジェクト情報を返すJSONエンドポイント

## 📋 主要なAPIエンドポイント

### 予約管理
- `GET /api/v1/reservations/` - 予約一覧
- `POST /api/v1/reservations/` - 予約作成
- `GET /api/v1/reservations/availability/slots` - 利用可能時間枠

### サービス管理
- `GET /api/v1/services/` - サービス一覧
- `GET /api/v1/services/{service_id}` - サービス詳細

### 商品管理
- `GET /api/v1/products/` - 商品一覧
- `GET /api/v1/products/{product_id}` - 商品詳細

### 注文管理
- `GET /api/v1/orders/` - 注文一覧
- `POST /api/v1/orders/` - 注文作成

### クーポン管理
- `GET /api/v1/coupons/` - クーポン一覧
- `POST /api/v1/coupons/validate` - クーポン検証

### キャンペーン管理
- `GET /api/v1/campaigns/active` - アクティブなキャンペーン

### スタイリスト管理
- `GET /api/v1/stylists/` - スタイリスト一覧
- `GET /api/v1/stylists/{stylist_id}` - スタイリスト詳細

### 顧客管理
- `GET /api/v1/customers/` - 顧客一覧
- `GET /api/v1/customers/{customer_id}` - 顧客詳細

### レコメンデーション
- `GET /api/v1/recommendations/services/{customer_id}` - おすすめサービス
- `GET /api/v1/recommendations/products/{customer_id}` - おすすめ商品
- `GET /api/v1/recommendations/times/{customer_id}` - おすすめ予約時間

### 招待管理
- `POST /api/v1/invitations/` - 招待作成
- `GET /api/v1/invitations/verify/{token}` - 招待検証
- `POST /api/v1/invitations/accept` - 招待承認・アカウント作成
- `GET /api/v1/invitations/` - 招待一覧

### 認証
- `POST /api/v1/auth/login` - ログイン
- `GET /api/v1/auth/me` - 現在の店舗情報取得

## 🚀 クイックアクセス

ブラウザで以下のURLを開いてください：

1. **ユーザーUI**: http://localhost:8000/
2. **APIドキュメント**: http://localhost:8000/docs
3. **ReDoc**: http://localhost:8000/redoc




