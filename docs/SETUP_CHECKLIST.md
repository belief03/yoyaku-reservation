# セットアップチェックリスト

このチェックリストに従って、段階的にセットアップを進めてください。

## 📝 事前準備

- [ ] Python 3.10以上がインストールされている
- [ ] Gitがインストールされている（オプション）
- [ ] テキストエディタまたはIDEが準備されている

## 🔧 Step 1: プロジェクトの準備

- [ ] プロジェクトディレクトリに移動
- [ ] 仮想環境を作成（推奨）
  ```bash
  python -m venv venv
  venv\Scripts\activate  # Windows
  ```
- [ ] 依存関係をインストール
  ```bash
  pip install -r requirements.txt
  ```

## 🌐 Step 2: Supabaseプロジェクトの作成

- [ ] Supabaseアカウントを作成
- [ ] 新しいプロジェクトを作成
- [ ] プロジェクト名を記録: `_________________`
- [ ] データベースパスワードを安全に保存

## 🔑 Step 3: 認証情報の取得

- [ ] Supabaseダッシュボードにログイン
- [ ] Settings → API に移動
- [ ] Project URLをコピー: `_________________`
- [ ] anon/public keyをコピー: `_________________`
- [ ] service_role keyをコピー（注意: 秘密に保管）: `_________________`

## 🗄️ Step 4: データベーススキーマの作成

- [ ] SQL Editorを開く
- [ ] `database/schema.sql`の内容をコピー
- [ ] SQL Editorに貼り付けて実行
- [ ] エラーがないことを確認
- [ ] テーブル一覧で以下が作成されていることを確認:
  - [ ] customers
  - [ ] stylists
  - [ ] services
  - [ ] products
  - [ ] reservations
  - [ ] orders
  - [ ] coupons
  - [ ] coupon_usages
  - [ ] campaigns

## 📦 Step 5: ストレージバケットの設定

- [ ] Storage → New bucket に移動
- [ ] バケット名: `uploads` で作成
- [ ] Public bucketにチェック（画像を公開する場合）
- [ ] バケットが作成されたことを確認

## ⚙️ Step 6: 環境変数の設定

- [ ] プロジェクトルートに`.env`ファイルを作成
- [ ] 以下の内容を記述:

```env
SUPABASE_URL=_________________
SUPABASE_KEY=_________________
SUPABASE_SERVICE_KEY=_________________
STORAGE_BUCKET=uploads
SECRET_KEY=_________________
```

- [ ] `.env`ファイルが`.gitignore`に含まれていることを確認

## ✅ Step 7: 動作確認

- [ ] 接続テストを実行
  ```bash
  python scripts/test_connection.py
  ```
- [ ] すべてのテストが成功することを確認
- [ ] APIサーバーを起動
  ```bash
  uvicorn api.main:app --reload
  ```
- [ ] ヘルスチェックにアクセス
  ```bash
  curl http://localhost:8000/health
  ```
- [ ] APIドキュメントにアクセス
  ```
  http://localhost:8000/docs
  ```

## 🧪 Step 8: テストデータの投入（オプション）

- [ ] `database/seed.sql`を実行（テストデータが必要な場合）
- [ ] データが正しく投入されたことを確認

## 📚 Step 9: ドキュメントの確認

- [ ] `README.md`を読む
- [ ] `docs/SUPABASE_SETUP.md`を読む
- [ ] APIエンドポイントの一覧を確認

## 🎉 完了！

すべてのチェックが完了したら、システムの使用を開始できます！

---

## 🆘 問題が発生した場合

1. `docs/SUPABASE_SETUP.md`のトラブルシューティングセクションを確認
2. エラーメッセージを確認
3. ログファイル（`logs/`ディレクトリ）を確認
4. Supabaseダッシュボードでプロジェクトの状態を確認






