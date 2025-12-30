"""
キャンペーンマネージャー
キャンペーンの実行と管理を行う
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from supabase import Client
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.supabase_client import supabase
from api.models import CampaignStatus
from config import settings


class CampaignManager:
    """キャンペーンマネージャークラス"""
    
    def __init__(self, db: Optional[Client] = None):
        """初期化"""
        self.db = db or supabase
    
    def get_active_campaigns(self) -> List[Dict]:
        """アクティブなキャンペーンを取得"""
        now = datetime.now().isoformat()
        
        result = self.db.table("campaigns").select("*").eq(
            "status", CampaignStatus.ACTIVE.value
        ).eq("is_active", True).lte("start_date", now).gte("end_date", now).execute()
        
        return result.data or []
    
    def check_campaign_eligibility(
        self,
        campaign_id: str,
        customer_id: str,
        order_amount: int
    ) -> tuple[bool, Optional[str], Optional[int]]:
        """
        顧客がキャンペーンの対象かどうかをチェック
        
        Returns:
            (eligible, message, discount_amount)
        """
        campaign = self.db.table("campaigns").select("*").eq("id", campaign_id).execute()
        
        if not campaign.data:
            return False, "キャンペーンが見つかりません", None
        
        campaign_data = campaign.data[0]
        
        # ステータスチェック
        if campaign_data["status"] != CampaignStatus.ACTIVE.value or not campaign_data.get("is_active"):
            return False, "キャンペーンは現在アクティブではありません", None
        
        # 期間チェック
        now = datetime.now()
        start_date = datetime.fromisoformat(campaign_data["start_date"])
        end_date = datetime.fromisoformat(campaign_data["end_date"])
        
        if now < start_date or now > end_date:
            return False, "キャンペーンの期間外です", None
        
        # 対象顧客チェック
        target_audience = campaign_data.get("target_audience")
        if target_audience:
            # 新規顧客のみ
            if target_audience.get("new_customers_only"):
                customer = self.db.table("customers").select("*").eq("id", customer_id).execute()
                if customer.data and customer.data[0].get("total_visits", 0) > 0:
                    return False, "このキャンペーンは新規顧客限定です", None
            
            # 特定の顧客グループ
            if target_audience.get("customer_ids"):
                if customer_id not in target_audience["customer_ids"]:
                    return False, "このキャンペーンの対象外です", None
        
        # 条件チェック
        conditions = campaign_data.get("conditions")
        if conditions:
            # 最低購入金額
            min_amount = conditions.get("min_purchase_amount")
            if min_amount and order_amount < min_amount:
                return False, f"最低購入金額 {min_amount}円以上でご利用いただけます", None
        
        # 割引金額の計算
        discount_amount = 0
        discount_type = campaign_data.get("discount_type")
        discount_value = campaign_data.get("discount_value")
        
        if discount_type == "percentage" and discount_value:
            discount_amount = int(order_amount * discount_value / 100)
        elif discount_type == "fixed_amount" and discount_value:
            discount_amount = discount_value
        
        return True, "キャンペーンが適用されました", discount_amount
    
    def apply_campaign_discount(
        self,
        campaign_id: str,
        customer_id: str,
        order_amount: int
    ) -> tuple[bool, Optional[int], Optional[str]]:
        """
        キャンペーン割引を適用
        
        Returns:
            (success, discount_amount, message)
        """
        eligible, message, discount_amount = self.check_campaign_eligibility(
            campaign_id, customer_id, order_amount
        )
        
        if not eligible:
            return False, None, message
        
        return True, discount_amount, message
    
    def update_campaign_status(self):
        """キャンペーンのステータスを自動更新"""
        now = datetime.now().isoformat()
        
        # 開始日時を過ぎたドラフトキャンペーンをアクティブに
        self.db.table("campaigns").update({
            "status": CampaignStatus.ACTIVE.value,
            "updated_at": now
        }).eq("status", CampaignStatus.DRAFT.value).lte("start_date", now).execute()
        
        # 終了日時を過ぎたアクティブキャンペーンを終了に
        self.db.table("campaigns").update({
            "status": CampaignStatus.ENDED.value,
            "is_active": False,
            "updated_at": now
        }).eq("status", CampaignStatus.ACTIVE.value).lt("end_date", now).execute()
    
    def get_campaign_statistics(self, campaign_id: str) -> Dict:
        """キャンペーンの統計情報を取得"""
        campaign = self.db.table("campaigns").select("*").eq("id", campaign_id).execute()
        
        if not campaign.data:
            return {}
        
        # 注文数と売上を集計（簡易版）
        # 実際の実装では、注文テーブルにキャンペーンIDを保存する必要があります
        
        return {
            "campaign_id": campaign_id,
            "name": campaign.data[0].get("name"),
            "status": campaign.data[0].get("status"),
            "start_date": campaign.data[0].get("start_date"),
            "end_date": campaign.data[0].get("end_date"),
            # 実際の実装では、注文データから集計
            "total_orders": 0,
            "total_revenue": 0,
            "total_discount": 0
        }
    
    def send_campaign_notification(self, campaign_id: str, customer_ids: List[str]) -> bool:
        """
        キャンペーンの通知を送信
        
        実際の実装では、メール送信やプッシュ通知などを実装
        """
        campaign = self.db.table("campaigns").select("*").eq("id", campaign_id).execute()
        
        if not campaign.data:
            return False
        
        # ここでメール送信やプッシュ通知のロジックを実装
        # 現在はプレースホルダー
        
        return True
    
    def create_automated_campaign(
        self,
        name: str,
        discount_type: str,
        discount_value: int,
        start_date: datetime,
        end_date: datetime,
        conditions: Optional[Dict] = None
    ) -> Dict:
        """自動化されたキャンペーンを作成"""
        campaign_data = {
            "name": name,
            "discount_type": discount_type,
            "discount_value": discount_value,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "status": CampaignStatus.DRAFT.value,
            "is_active": True,
            "conditions": conditions or {}
        }
        
        result = self.db.table("campaigns").insert(campaign_data).execute()
        
        if result.data:
            return result.data[0]
        return {}


def get_campaign_manager(db: Optional[Client] = None) -> CampaignManager:
    """キャンペーンマネージャーのインスタンスを取得"""
    return CampaignManager(db)







