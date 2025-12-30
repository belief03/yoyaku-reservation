-- 設定テーブルの作成
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックスの作成
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);

-- デフォルト設定の挿入
INSERT INTO settings (key, value) 
VALUES (
    'shop_settings',
    '{"shop_name": "Yoyaku 予約システム", "primary_color": "#667eea", "secondary_color": "#764ba2"}'
)
ON CONFLICT (key) DO NOTHING;





