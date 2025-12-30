"""
レコメンデーションエンジン
顧客に最適なサービスや商品を推薦する
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from supabase import Client
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.supabase_client import supabase
from config import settings


class RecommendationEngine:
    """レコメンデーションエンジンクラス"""
    
    def __init__(self, db: Optional[Client] = None):
        """初期化"""
        self.db = db or supabase
        self.use_ai = settings.AI_ENABLED and settings.OPENAI_API_KEY
    
    def recommend_services(
        self,
        customer_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        顧客に最適なサービスを推薦
        
        Args:
            customer_id: 顧客ID
            limit: 推薦するサービスの数
        
        Returns:
            推薦サービスのリスト
        """
        # 顧客情報の取得
        customer = self.db.table("customers").select("*").eq("id", customer_id).execute()
        if not customer.data:
            return []
        
        customer_data = customer.data[0]
        
        # 過去の予約履歴を取得
        reservations = self.db.table("reservations").select(
            "service_id, reservation_datetime, status"
        ).eq("customer_id", customer_id).in_(
            "status", ["completed", "confirmed"]
        ).order("reservation_datetime", desc=True).limit(10).execute()
        
        # 過去に利用したサービスのIDを取得
        used_service_ids = [r["service_id"] for r in reservations.data]
        
        # アクティブなサービスを取得
        services = self.db.table("services").select("*").eq(
            "is_active", True
        ).order("display_order", desc=False).execute()
        
        if not services.data:
            return []
        
        # 推薦ロジック（簡易版）
        # 1. 過去に利用したサービスを優先
        # 2. 人気のサービスを推薦
        # 3. 新規サービスを推薦
        
        recommended = []
        
        # 過去に利用したサービス
        for service in services.data:
            if service["id"] in used_service_ids:
                recommended.append({
                    **service,
                    "reason": "過去にご利用いただいたサービス",
                    "score": 0.9
                })
        
        # 人気のサービス（予約数が多い）
        popular_services = self._get_popular_services(limit=limit)
        for service in popular_services:
            if service["id"] not in [s["id"] for s in recommended]:
                recommended.append({
                    **service,
                    "reason": "人気のサービス",
                    "score": 0.7
                })
        
        # 新規サービス
        new_services = self.db.table("services").select("*").eq(
            "is_active", True
        ).order("created_at", desc=True).limit(3).execute()
        
        for service in new_services.data:
            if service["id"] not in [s["id"] for s in recommended]:
                recommended.append({
                    **service,
                    "reason": "新着サービス",
                    "score": 0.6
                })
        
        # スコアでソートして上位を返す
        recommended.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return recommended[:limit]
    
    def _get_popular_services(self, limit: int = 5) -> List[Dict]:
        """人気のサービスを取得"""
        # 予約数の多いサービスを取得
        reservations = self.db.table("reservations").select(
            "service_id"
        ).in_("status", ["completed", "confirmed"]).execute()
        
        # サービスIDごとにカウント
        service_counts = {}
        for r in reservations.data:
            service_id = r["service_id"]
            service_counts[service_id] = service_counts.get(service_id, 0) + 1
        
        # カウントでソート
        sorted_services = sorted(
            service_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # サービス詳細を取得
        popular_services = []
        for service_id, count in sorted_services:
            service = self.db.table("services").select("*").eq("id", service_id).execute()
            if service.data:
                popular_services.append(service.data[0])
        
        return popular_services
    
    def recommend_products(
        self,
        customer_id: str,
        service_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        顧客に最適な商品を推薦
        
        Args:
            customer_id: 顧客ID
            service_id: 関連するサービスID（オプション）
            limit: 推薦する商品の数
        
        Returns:
            推薦商品のリスト
        """
        # アクティブな商品を取得
        products = self.db.table("products").select("*").eq(
            "is_active", True
        ).order("display_order", desc=False).execute()
        
        if not products.data:
            return []
        
        recommended = []
        
        # 在庫がある商品を優先
        in_stock_products = [
            p for p in products.data
            if p.get("stock_quantity") is None or p.get("stock_quantity", 0) > 0
        ]
        
        # サービスに関連する商品（カテゴリが一致する場合）
        if service_id:
            service = self.db.table("services").select("*").eq("id", service_id).execute()
            if service.data and service.data[0].get("category"):
                service_category = service.data[0]["category"]
                for product in in_stock_products:
                    if product.get("category") == service_category:
                        recommended.append({
                            **product,
                            "reason": f"{service.data[0]['name']}に関連する商品",
                            "score": 0.8
                        })
        
        # 人気の商品
        popular_products = self._get_popular_products(limit=limit)
        for product in popular_products:
            if product["id"] not in [p["id"] for p in recommended]:
                recommended.append({
                    **product,
                    "reason": "人気の商品",
                    "score": 0.7
                })
        
        # 新規商品
        new_products = self.db.table("products").select("*").eq(
            "is_active", True
        ).order("created_at", desc=True).limit(3).execute()
        
        for product in new_products.data:
            if product["id"] not in [p["id"] for p in recommended]:
                recommended.append({
                    **product,
                    "reason": "新着商品",
                    "score": 0.6
                })
        
        # スコアでソートして上位を返す
        recommended.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return recommended[:limit]
    
    def _get_popular_products(self, limit: int = 5) -> List[Dict]:
        """人気の商品を取得"""
        # 注文数の多い商品を取得
        orders = self.db.table("orders").select("items").in_(
            "status", ["paid", "completed"]
        ).execute()
        
        # 商品IDごとにカウント
        product_counts = {}
        for order in orders.data:
            if order.get("items"):
                for item in order["items"]:
                    if item.get("product_id"):
                        product_id = item["product_id"]
                        quantity = item.get("quantity", 1)
                        product_counts[product_id] = product_counts.get(product_id, 0) + quantity
        
        # カウントでソート
        sorted_products = sorted(
            product_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # 商品詳細を取得
        popular_products = []
        for product_id, count in sorted_products:
            product = self.db.table("products").select("*").eq("id", product_id).execute()
            if product.data:
                popular_products.append(product.data[0])
        
        return popular_products
    
    def predict_optimal_time(
        self,
        customer_id: str,
        service_id: str
    ) -> List[Dict]:
        """
        顧客にとって最適な予約時間を予測
        
        Returns:
            推奨時間のリスト
        """
        # 顧客の過去の予約時間を分析
        reservations = self.db.table("reservations").select(
            "reservation_datetime"
        ).eq("customer_id", customer_id).in_(
            "status", ["completed", "confirmed"]
        ).order("reservation_datetime", desc=True).limit(10).execute()
        
        # 時間帯の傾向を分析
        time_preferences = {}
        for r in reservations.data:
            dt = datetime.fromisoformat(r["reservation_datetime"])
            hour = dt.hour
            time_preferences[hour] = time_preferences.get(hour, 0) + 1
        
        # 最も利用された時間帯を取得
        if time_preferences:
            preferred_hour = max(time_preferences.items(), key=lambda x: x[1])[0]
        else:
            preferred_hour = 14  # デフォルトは14時
        
        # 推奨時間を生成（次の1週間）
        recommendations = []
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for day_offset in range(7):
            target_date = today + timedelta(days=day_offset)
            target_datetime = target_date.replace(hour=preferred_hour, minute=0)
            
            # 営業時間内かチェック
            start_hour = int(settings.BUSINESS_HOURS_START.split(':')[0])
            end_hour = int(settings.BUSINESS_HOURS_END.split(':')[0])
            
            if start_hour <= preferred_hour < end_hour:
                recommendations.append({
                    "datetime": target_datetime.isoformat(),
                    "reason": "過去のご利用パターンに基づく推奨時間",
                    "score": 0.8
                })
        
        return recommendations[:5]  # 上位5つを返す
    
    def analyze_customer_preferences(self, customer_id: str) -> Dict:
        """
        顧客の好みを分析
        
        Returns:
            顧客の好みに関する分析結果
        """
        # 予約履歴を取得
        reservations = self.db.table("reservations").select(
            "service_id, stylist_id, reservation_datetime"
        ).eq("customer_id", customer_id).in_(
            "status", ["completed", "confirmed"]
        ).execute()
        
        if not reservations.data:
            return {
                "total_visits": 0,
                "preferred_services": [],
                "preferred_stylists": [],
                "preferred_time": None
            }
        
        # サービス分析
        service_counts = {}
        for r in reservations.data:
            service_id = r["service_id"]
            service_counts[service_id] = service_counts.get(service_id, 0) + 1
        
        preferred_services = sorted(
            service_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # スタイリスト分析
        stylist_counts = {}
        for r in reservations.data:
            if r.get("stylist_id"):
                stylist_id = r["stylist_id"]
                stylist_counts[stylist_id] = stylist_counts.get(stylist_id, 0) + 1
        
        preferred_stylists = sorted(
            stylist_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # 時間帯分析
        hour_counts = {}
        for r in reservations.data:
            dt = datetime.fromisoformat(r["reservation_datetime"])
            hour = dt.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        preferred_hour = None
        if hour_counts:
            preferred_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        
        return {
            "total_visits": len(reservations.data),
            "preferred_services": [s[0] for s in preferred_services],
            "preferred_stylists": [s[0] for s in preferred_stylists],
            "preferred_time": preferred_hour
        }


def get_recommendation_engine(db: Optional[Client] = None) -> RecommendationEngine:
    """レコメンデーションエンジンのインスタンスを取得"""
    return RecommendationEngine(db)







