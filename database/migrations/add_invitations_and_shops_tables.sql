-- 招待テーブルの作成
CREATE TABLE IF NOT EXISTS invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    invitation_url TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ,
    shop_id UUID,
    shop_name VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 店舗テーブルの作成
CREATE TABLE IF NOT EXISTS shops (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    admin_email VARCHAR(255) NOT NULL,
    admin_name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックスの作成
CREATE INDEX IF NOT EXISTS idx_invitations_token ON invitations(token);
CREATE INDEX IF NOT EXISTS idx_invitations_email ON invitations(email);
CREATE INDEX IF NOT EXISTS idx_invitations_used ON invitations(used);
CREATE INDEX IF NOT EXISTS idx_shops_email ON shops(email);
CREATE INDEX IF NOT EXISTS idx_shops_is_active ON shops(is_active);

-- 招待URL検証用の関数（オプション）
CREATE OR REPLACE FUNCTION is_invitation_valid(invitation_token VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM invitations
        WHERE token = invitation_token
        AND used = FALSE
        AND expires_at > NOW()
    );
END;
$$ LANGUAGE plpgsql;





