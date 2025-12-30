"""
既存の招待一覧を表示するスクリプト
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

try:
    headers = {}
    if ADMIN_API_KEY:
        headers["X-Admin-API-Key"] = ADMIN_API_KEY
    
    response = requests.get(f"{API_BASE}/invitations/", headers=headers)
    if response.status_code == 200:
        invitations = response.json()
        
        print("=" * 60)
        print("既存の招待一覧")
        print("=" * 60)
        
        if not invitations:
            print("[INFO] 招待は存在しません")
        else:
            unused_invitations = [inv for inv in invitations if not inv.get('used', False)]
            
            if unused_invitations:
                print(f"\n[INFO] 未使用の招待: {len(unused_invitations)}件\n")
                for inv in unused_invitations:
                    print(f"[EMAIL] メールアドレス: {inv['email']}")
                    if inv.get('shop_name'):
                        print(f"[SHOP] 店舗名: {inv['shop_name']}")
                    print(f"[URL] 招待URL: {inv['invitation_url']}")
                    print(f"[TOKEN] トークン: {inv['token']}")
                    print(f"[EXPIRES] 有効期限: {inv['expires_at']}")
                    print("-" * 60)
            else:
                print("[INFO] 未使用の招待はありません")
            
            used_invitations = [inv for inv in invitations if inv.get('used', False)]
            if used_invitations:
                print(f"\n[INFO] 使用済みの招待: {len(used_invitations)}件")
    else:
        print(f"[ERROR] エラー: {response.status_code}")
        print(f"   詳細: {response.text}")
except requests.exceptions.ConnectionError:
    print("[ERROR] サーバーに接続できません。サーバーが起動しているか確認してください。")
except Exception as e:
    print(f"[ERROR] エラーが発生しました: {str(e)}")

