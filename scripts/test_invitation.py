"""
招待リンクのテスト用スクリプト
招待を作成して、招待URLを表示します
"""
import requests
import json
import sys
import io
import os

# Windowsコンソールの文字エンコーディング問題を回避
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API_BASE = "http://localhost:8000/api/v1"
# システム管理者のAPIキー（環境変数から取得、開発環境では設定不要）
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

def create_invitation(email: str, shop_name: str = None):
    """招待を作成"""
    url = f"{API_BASE}/invitations/"
    data = {
        "email": email,
        "expires_in_days": 7
    }
    if shop_name:
        data["shop_name"] = shop_name
    
    try:
        headers = {"Content-Type": "application/json"}
        if ADMIN_API_KEY:
            headers["X-Admin-API-Key"] = ADMIN_API_KEY
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("\n[OK] 招待が作成されました！")
            print(f"[EMAIL] メールアドレス: {result['email']}")
            print(f"[URL] 招待URL: {result['invitation_url']}")
            print(f"[TOKEN] トークン: {result['token']}")
            print(f"[EXPIRES] 有効期限: {result['expires_at']}")
            print(f"\n[INFO] ブラウザで以下のURLにアクセスしてください:")
            print(f"   {result['invitation_url']}")
            return result
        else:
            print(f"[ERROR] エラー: {response.status_code}")
            print(f"   詳細: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("[ERROR] サーバーに接続できません。サーバーが起動しているか確認してください。")
        print(f"   URL: {API_BASE}")
        return None
    except Exception as e:
        print(f"[ERROR] エラーが発生しました: {str(e)}")
        return None

def verify_invitation(token: str):
    """招待を検証"""
    url = f"{API_BASE}/invitations/verify/{token}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print("\n[OK] 招待は有効です")
            print(f"[EMAIL] メールアドレス: {result['email']}")
            if result.get('shop_name'):
                print(f"[SHOP] 店舗名: {result['shop_name']}")
            return result
        else:
            print(f"[ERROR] エラー: {response.status_code}")
            print(f"   詳細: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] エラーが発生しました: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python scripts/test_invitation.py <email> [shop_name]")
        print("\n例:")
        print("  python scripts/test_invitation.py test@example.com")
        print("  python scripts/test_invitation.py test@example.com \"テスト店舗\"")
        sys.exit(1)
    
    email = sys.argv[1]
    shop_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("=" * 60)
    print("招待リンクテストスクリプト")
    print("=" * 60)
    
    result = create_invitation(email, shop_name)
    
    if result:
        print("\n" + "=" * 60)
        print("検証テスト")
        print("=" * 60)
        verify_invitation(result['token'])

