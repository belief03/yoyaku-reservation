"""
システム動作確認スクリプト
すべての主要なエンドポイントと機能をテストします
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

# WindowsでのUnicodeエラーを防ぐ
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import requests
from typing import Dict, List, Tuple

API_BASE = "http://localhost:8000"
API_V1 = f"{API_BASE}/api/v1"

# テスト結果を記録
test_results: List[Dict] = []


def print_header(text: str):
    """ヘッダーを表示"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_test(name: str, status: str, details: str = ""):
    """テスト結果を表示"""
    status_symbol = "[OK]" if status == "PASS" else "[NG]" if status == "FAIL" else "[WARN]"
    print(f"{status_symbol} {name}")
    if details:
        print(f"   {details}")
    
    test_results.append({
        "name": name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })


def test_endpoint(method: str, endpoint: str, expected_status: int = 200, 
                  data: dict = None, params: dict = None) -> Tuple[bool, dict]:
    """エンドポイントをテスト"""
    try:
        url = f"{API_BASE}{endpoint}"
        if method.upper() == "GET":
            response = requests.get(url, params=params, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method.upper() == "PATCH":
            response = requests.patch(url, json=data, timeout=5)
        elif method.upper() == "DELETE":
            response = requests.delete(url, timeout=5)
        else:
            return False, {"error": f"Unsupported method: {method}"}
        
        success = response.status_code == expected_status
        try:
            response_data = response.json()
        except:
            response_data = {"text": response.text}
        
        return success, {
            "status_code": response.status_code,
            "data": response_data
        }
    except requests.exceptions.ConnectionError:
        return False, {"error": "サーバーに接続できません。サーバーが起動しているか確認してください。"}
    except Exception as e:
        return False, {"error": str(e)}


def main():
    """メインのテスト実行"""
    print_header("Yoyaku Reservation System - システム動作確認")
    
    # 1. 基本情報の確認
    print_header("1. 基本情報")
    
    success, result = test_endpoint("GET", "/")
    if success and result["data"].get("status") == "running":
        print_test("ルートエンドポイント", "PASS", f"Version: {result['data'].get('version')}")
    else:
        print_test("ルートエンドポイント", "FAIL", str(result))
    
    success, result = test_endpoint("GET", "/health")
    if success and result["data"].get("status") == "healthy":
        print_test("ヘルスチェック", "PASS")
    else:
        print_test("ヘルスチェック", "FAIL", str(result))
    
    # 2. サービス管理
    print_header("2. サービス管理")
    
    success, result = test_endpoint("GET", "/api/v1/services/")
    if success:
        items = result["data"].get("items", [])
        print_test("サービス一覧取得", "PASS", f"{len(items)}件のサービスを取得")
    else:
        print_test("サービス一覧取得", "FAIL", str(result))
    
    # 3. スタイリスト管理
    print_header("3. スタイリスト管理")
    
    success, result = test_endpoint("GET", "/api/v1/stylists/")
    if success:
        items = result["data"].get("items", [])
        print_test("スタイリスト一覧取得", "PASS", f"{len(items)}件のスタイリストを取得")
        if items:
            stylist_id = items[0].get("id")
            if stylist_id:
                success2, result2 = test_endpoint("GET", f"/api/v1/stylists/{stylist_id}")
                if success2:
                    print_test("スタイリスト詳細取得", "PASS")
                else:
                    print_test("スタイリスト詳細取得", "FAIL", str(result2))
    else:
        print_test("スタイリスト一覧取得", "FAIL", str(result))
    
    # 4. 顧客管理
    print_header("4. 顧客管理")
    
    success, result = test_endpoint("GET", "/api/v1/customers/")
    if success:
        items = result["data"].get("items", [])
        print_test("顧客一覧取得", "PASS", f"{len(items)}件の顧客を取得")
        if items:
            customer_id = items[0].get("id")
            if customer_id:
                success2, result2 = test_endpoint("GET", f"/api/v1/customers/{customer_id}")
                if success2:
                    print_test("顧客詳細取得", "PASS")
                else:
                    print_test("顧客詳細取得", "FAIL", str(result2))
    else:
        print_test("顧客一覧取得", "FAIL", str(result))
    
    # 5. 商品管理
    print_header("5. 商品管理")
    
    success, result = test_endpoint("GET", "/api/v1/products/")
    if success:
        items = result["data"].get("items", [])
        print_test("商品一覧取得", "PASS", f"{len(items)}件の商品を取得")
    else:
        print_test("商品一覧取得", "FAIL", str(result))
    
    # 6. 予約管理
    print_header("6. 予約管理")
    
    success, result = test_endpoint("GET", "/api/v1/reservations/")
    if success:
        items = result["data"].get("items", [])
        print_test("予約一覧取得", "PASS", f"{len(items)}件の予約を取得")
    else:
        print_test("予約一覧取得", "FAIL", str(result))
    
    # 利用可能時間枠の確認
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    success, result = test_endpoint("GET", "/api/v1/reservations/availability/slots", 
                                   params={"date": tomorrow})
    if success:
        slots = result["data"].get("slots", [])
        available_slots = [s for s in slots if s.get("available")]
        print_test("利用可能時間枠取得", "PASS", 
                  f"{len(available_slots)}/{len(slots)}の時間枠が利用可能")
    else:
        print_test("利用可能時間枠取得", "FAIL", str(result))
    
    # 7. 注文管理
    print_header("7. 注文管理")
    
    success, result = test_endpoint("GET", "/api/v1/orders/")
    if success:
        items = result["data"].get("items", [])
        print_test("注文一覧取得", "PASS", f"{len(items)}件の注文を取得")
    else:
        print_test("注文一覧取得", "FAIL", str(result))
    
    # 8. クーポン管理
    print_header("8. クーポン管理")
    
    success, result = test_endpoint("GET", "/api/v1/coupons/")
    if success:
        items = result["data"].get("items", [])
        print_test("クーポン一覧取得", "PASS", f"{len(items)}件のクーポンを取得")
    else:
        print_test("クーポン一覧取得", "FAIL", str(result))
    
    # 9. キャンペーン管理
    print_header("9. キャンペーン管理")
    
    success, result = test_endpoint("GET", "/api/v1/campaigns/")
    if success:
        items = result["data"].get("items", [])
        print_test("キャンペーン一覧取得", "PASS", f"{len(items)}件のキャンペーンを取得")
    else:
        print_test("キャンペーン一覧取得", "FAIL", str(result))
    
    success, result = test_endpoint("GET", "/api/v1/campaigns/active")
    if success:
        campaigns = result["data"].get("campaigns", [])
        print_test("アクティブキャンペーン取得", "PASS", f"{len(campaigns)}件のアクティブキャンペーン")
    else:
        print_test("アクティブキャンペーン取得", "FAIL", str(result))
    
    # 10. ストレージ
    print_header("10. ストレージ管理")
    
    success, result = test_endpoint("GET", "/api/v1/storage/list")
    if success:
        files = result["data"].get("files", [])
        print_test("ファイル一覧取得", "PASS", f"{len(files)}件のファイル")
    else:
        print_test("ファイル一覧取得", "FAIL", str(result))
    
    # 結果サマリー
    print_header("テスト結果サマリー")
    
    total = len(test_results)
    passed = len([r for r in test_results if r["status"] == "PASS"])
    failed = len([r for r in test_results if r["status"] == "FAIL"])
    
    print(f"総テスト数: {total}")
    print(f"[OK] 成功: {passed}")
    print(f"[NG] 失敗: {failed}")
    print(f"成功率: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\n失敗したテスト:")
        for result in test_results:
            if result["status"] == "FAIL":
                print(f"  [NG] {result['name']}: {result['details']}")
    
    # 結果をJSONファイルに保存
    report_file = project_root / "test_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": passed/total*100 if total > 0 else 0
            },
            "results": test_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n詳細なテスト結果は {report_file} に保存されました。")
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nテストが中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n予期しないエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

