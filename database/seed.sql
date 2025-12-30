-- ============================================
-- Yoyaku Reservation System Seed Data
-- ============================================
-- テスト用の初期データを投入します
-- 本番環境では実行しないでください

-- ============================================
-- 顧客データ
-- ============================================
INSERT INTO customers (id, email, phone, name, name_kana, is_active) VALUES
('00000000-0000-0000-0000-000000000001', 'customer1@example.com', '090-1234-5678', '山田 太郎', 'ヤマダ タロウ', TRUE),
('00000000-0000-0000-0000-000000000002', 'customer2@example.com', '090-2345-6789', '佐藤 花子', 'サトウ ハナコ', TRUE),
('00000000-0000-0000-0000-000000000003', 'customer3@example.com', '090-3456-7890', '鈴木 一郎', 'スズキ イチロウ', TRUE)
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- スタイリストデータ
-- ============================================
INSERT INTO stylists (id, name, name_kana, email, specialty, is_active) VALUES
('10000000-0000-0000-0000-000000000001', '田中 美咲', 'タナカ ミサキ', 'stylist1@example.com', 'カット・カラー', TRUE),
('10000000-0000-0000-0000-000000000002', '中村 健太', 'ナカムラ ケンタ', 'stylist2@example.com', 'パーマ・ストレート', TRUE),
('10000000-0000-0000-0000-000000000003', '小林 さくら', 'コバヤシ サクラ', 'stylist3@example.com', 'ヘアケア', TRUE)
ON CONFLICT DO NOTHING;

-- ============================================
-- サービスデータ
-- ============================================
INSERT INTO services (id, name, name_en, description, duration_minutes, price, category, display_order, is_active) VALUES
('20000000-0000-0000-0000-000000000001', 'カット', 'Cut', 'スタンダードカット', 30, 3000, 'カット', 1, TRUE),
('20000000-0000-0000-0000-000000000002', 'カット+カラー', 'Cut + Color', 'カットとカラーのセット', 90, 8000, 'カット・カラー', 2, TRUE),
('20000000-0000-0000-0000-000000000003', 'パーマ', 'Perm', 'スタンダードパーマ', 120, 6000, 'パーマ', 3, TRUE),
('20000000-0000-0000-0000-000000000004', 'ストレートパーマ', 'Straight Perm', 'ストレートパーマ', 120, 7000, 'パーマ', 4, TRUE),
('20000000-0000-0000-0000-000000000005', 'トリートメント', 'Treatment', 'ヘアトリートメント', 30, 2000, 'ヘアケア', 5, TRUE)
ON CONFLICT DO NOTHING;

-- ============================================
-- 商品データ
-- ============================================
INSERT INTO products (id, name, name_en, description, price, category, stock_quantity, display_order, is_active) VALUES
('30000000-0000-0000-0000-000000000001', 'シャンプー', 'Shampoo', '高品質シャンプー', 1500, 'ヘアケア', 50, 1, TRUE),
('30000000-0000-0000-0000-000000000002', 'コンディショナー', 'Conditioner', '高品質コンディショナー', 1500, 'ヘアケア', 50, 2, TRUE),
('30000000-0000-0000-0000-000000000003', 'ヘアオイル', 'Hair Oil', '栄養補給ヘアオイル', 2500, 'ヘアケア', 30, 3, TRUE),
('30000000-0000-0000-0000-000000000004', 'スタイリング剤', 'Styling Product', 'スタイリング剤', 2000, 'スタイリング', 40, 4, TRUE)
ON CONFLICT DO NOTHING;

-- ============================================
-- クーポンデータ
-- ============================================
INSERT INTO coupons (id, code, name, description, coupon_type, discount_value, valid_from, valid_until, usage_limit, is_active) VALUES
('40000000-0000-0000-0000-000000000001', 'WELCOME10', '新規顧客10%オフ', '新規顧客限定10%オフクーポン', 'percentage', 10, NOW(), NOW() + INTERVAL '1 year', 100, TRUE),
('40000000-0000-0000-0000-000000000002', 'SAVE500', '500円オフ', '500円割引クーポン', 'fixed_amount', 500, NOW(), NOW() + INTERVAL '6 months', 50, TRUE),
('40000000-0000-0000-0000-000000000003', 'FIRST20', '初回20%オフ', '初回利用限定20%オフ', 'percentage', 20, NOW(), NOW() + INTERVAL '3 months', 30, TRUE)
ON CONFLICT (code) DO NOTHING;

-- ============================================
-- キャンペーンデータ
-- ============================================
INSERT INTO campaigns (id, name, description, status, start_date, end_date, discount_type, discount_value, is_active) VALUES
('50000000-0000-0000-0000-000000000001', '春のキャンペーン', '春の新生活応援キャンペーン', 'active', NOW(), NOW() + INTERVAL '3 months', 'percentage', 15, TRUE),
('50000000-0000-0000-0000-000000000002', '新規顧客キャンペーン', '新規顧客限定キャンペーン', 'active', NOW(), NOW() + INTERVAL '6 months', 'percentage', 20, TRUE)
ON CONFLICT DO NOTHING;






