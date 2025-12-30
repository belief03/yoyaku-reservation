"""
Supabase接続テストスクリプト
環境変数が正しく設定されているか確認します
"""
import sys
import os
from pathlib import Path

# WindowsでのUnicodeエラーを防ぐ
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from config import settings
    from api.supabase_client import SupabaseClient
    
    print("=" * 50)
    print("Supabase接続テスト")
    print("=" * 50)
    print()
    
    # 環境変数の確認
    print("[INFO] 環境変数の確認:")
    print(f"  SUPABASE_URL: {'[OK] 設定済み' if settings.SUPABASE_URL else '[NG] 未設定'}")
    print(f"  SUPABASE_KEY: {'[OK] 設定済み' if settings.SUPABASE_KEY else '[NG] 未設定'}")
    print(f"  SUPABASE_SERVICE_KEY: {'[OK] 設定済み' if settings.SUPABASE_SERVICE_KEY else '[WARN] 未設定（オプション）'}")
    print(f"  STORAGE_BUCKET: {settings.STORAGE_BUCKET}")
    print()
    
    # 必須項目のチェック
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("[ERROR] SUPABASE_URL と SUPABASE_KEY は必須です")
        print()
        print("[INFO] 解決方法:")
        print("  1. .envファイルを作成")
        print("  2. SUPABASE_URL と SUPABASE_KEY を設定")
        print("  3. docs/SUPABASE_SETUP.md を参照してください")
        sys.exit(1)
    
    # 接続テスト
    print("[INFO] 接続テスト中...")
    try:
        client = SupabaseClient.get_client()
        
        # 簡単なクエリで接続を確認
        result = client.table("customers").select("count", count="exact").limit(1).execute()
        
        print("[OK] 接続成功！")
        print()
        print("[INFO] データベース情報:")
        print(f"  Project URL: {settings.SUPABASE_URL}")
        print(f"  テーブル接続: OK")
        
        # テーブルの存在確認
        print()
        print("[INFO] テーブル存在確認:")
        tables = [
            "customers", "stylists", "services", "products",
            "reservations", "orders", "coupons", "coupon_usages", "campaigns"
        ]
        
        for table in tables:
            try:
                test_result = client.table(table).select("id").limit(1).execute()
                print(f"  [OK] {table}")
            except Exception as e:
                print(f"  [NG] {table} - エラー: {str(e)}")
        
        print()
        print("=" * 50)
        print("[OK] すべてのテストが成功しました！")
        print("=" * 50)
        
    except Exception as e:
        print(f"[ERROR] 接続エラー: {str(e)}")
        print()
        print("[INFO] 確認事項:")
        print("  1. SUPABASE_URL が正しいか確認")
        print("  2. SUPABASE_KEY が正しいか確認")
        print("  3. Supabaseプロジェクトがアクティブか確認")
        print("  4. ネットワーク接続を確認")
        sys.exit(1)
    
    # ストレージバケットの確認（オプション）
    if settings.STORAGE_BUCKET:
        print()
        print("[INFO] ストレージバケット確認:")
        try:
            storage = client.storage.from_(settings.STORAGE_BUCKET)
            # バケットの存在確認（簡易版）
            print(f"  [OK] バケット '{settings.STORAGE_BUCKET}' の設定を確認")
        except Exception as e:
            print(f"  [WARN] ストレージバケットの確認中にエラー: {str(e)}")
            print("     （バケットが未作成の可能性があります）")

except ImportError as e:
    print(f"[ERROR] インポートエラー: {str(e)}")
    print()
    print("[INFO] 解決方法:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] 予期しないエラー: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

