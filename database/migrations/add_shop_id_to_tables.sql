-- 各テーブルにshop_idカラムを追加するマイグレーション
-- 招待された店舗だけが使えるシステムを構築するため

-- 顧客テーブルにshop_idを追加
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS shop_id VARCHAR(255);

-- スタイリストテーブルにshop_idを追加
ALTER TABLE stylists 
ADD COLUMN IF NOT EXISTS shop_id VARCHAR(255);

-- サービステーブルにshop_idを追加
ALTER TABLE services 
ADD COLUMN IF NOT EXISTS shop_id VARCHAR(255);

-- 商品テーブルにshop_idを追加
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS shop_id VARCHAR(255);

-- 予約テーブルにshop_idを追加
ALTER TABLE reservations 
ADD COLUMN IF NOT EXISTS shop_id VARCHAR(255);

-- 注文テーブルにshop_idを追加
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS shop_id VARCHAR(255);

-- クーポンテーブルにshop_idを追加
ALTER TABLE coupons 
ADD COLUMN IF NOT EXISTS shop_id VARCHAR(255);

-- クーポン使用履歴テーブルにshop_idを追加
ALTER TABLE coupon_usages 
ADD COLUMN IF NOT EXISTS shop_id VARCHAR(255);

-- キャンペーンテーブルにshop_idを追加
ALTER TABLE campaigns 
ADD COLUMN IF NOT EXISTS shop_id VARCHAR(255);

-- インデックスの作成（パフォーマンス向上のため）
CREATE INDEX IF NOT EXISTS idx_customers_shop_id ON customers(shop_id);
CREATE INDEX IF NOT EXISTS idx_stylists_shop_id ON stylists(shop_id);
CREATE INDEX IF NOT EXISTS idx_services_shop_id ON services(shop_id);
CREATE INDEX IF NOT EXISTS idx_products_shop_id ON products(shop_id);
CREATE INDEX IF NOT EXISTS idx_reservations_shop_id ON reservations(shop_id);
CREATE INDEX IF NOT EXISTS idx_orders_shop_id ON orders(shop_id);
CREATE INDEX IF NOT EXISTS idx_coupons_shop_id ON coupons(shop_id);
CREATE INDEX IF NOT EXISTS idx_coupon_usages_shop_id ON coupon_usages(shop_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_shop_id ON campaigns(shop_id);

-- 既存データがある場合、shop_idをNULLのままにしておく（テストデータがない状態を想定）
-- 本番環境では、既存データに適切なshop_idを設定する必要があります




