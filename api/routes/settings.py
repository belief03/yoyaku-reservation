"""
店舗設定管理APIルート
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from supabase import Client
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api.database import get_db
from api.logger import logger

router = APIRouter()


class ShopSettings(BaseModel):
    """店舗設定モデル"""
    shop_name: str
    shop_logo_url: Optional[str] = None
    shop_address: Optional[str] = None
    shop_phone: Optional[str] = None
    shop_email: Optional[str] = None
    shop_description: Optional[str] = None
    
    # テーマ設定
    primary_color: str = "#667eea"
    secondary_color: str = "#764ba2"
    accent_color: Optional[str] = None
    
    # 営業時間設定
    business_hours_start: str = "09:00"
    business_hours_end: str = "20:00"
    business_days: list[int] = [0, 1, 2, 3, 4, 5, 6]  # 0=月曜日
    
    # 予約設定
    reservation_slot_duration_minutes: int = 30
    max_advance_booking_days: int = 90
    min_advance_booking_hours: int = 2
    cancellation_hours_before: int = 24
    
    # その他設定
    enable_email_notifications: bool = True
    enable_sms_notifications: bool = False
    currency: str = "JPY"
    timezone: str = "Asia/Tokyo"
    
    # カスタムCSS/JS
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None


class ShopSettingsUpdate(BaseModel):
    """店舗設定更新モデル"""
    shop_name: Optional[str] = None
    shop_logo_url: Optional[str] = None
    shop_address: Optional[str] = None
    shop_phone: Optional[str] = None
    shop_email: Optional[str] = None
    shop_description: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    business_hours_start: Optional[str] = None
    business_hours_end: Optional[str] = None
    business_days: Optional[list[int]] = None
    reservation_slot_duration_minutes: Optional[int] = None
    max_advance_booking_days: Optional[int] = None
    min_advance_booking_hours: Optional[int] = None
    cancellation_hours_before: Optional[int] = None
    enable_email_notifications: Optional[bool] = None
    enable_sms_notifications: Optional[bool] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None


@router.get("/", response_model=ShopSettings)
async def get_settings(db: Client = Depends(get_db)):
    """店舗設定を取得"""
    try:
        # settingsテーブルから取得（存在しない場合はデフォルト値を返す）
        result = db.table("settings").select("*").eq("key", "shop_settings").execute()
        
        if result.data and len(result.data) > 0:
            settings_data = json.loads(result.data[0].get("value", "{}"))
            return ShopSettings(**settings_data)
        else:
            # デフォルト設定を返す
            return ShopSettings(shop_name="Yoyaku 予約システム")
    except Exception as e:
        logger.error(f"設定取得エラー: {str(e)}")
        # エラー時もデフォルト値を返す
        return ShopSettings(shop_name="Yoyaku 予約システム")


@router.put("/", response_model=ShopSettings)
async def update_settings(
    settings_update: ShopSettingsUpdate,
    db: Client = Depends(get_db)
):
    """店舗設定を更新"""
    try:
        # 既存の設定を取得
        existing_result = db.table("settings").select("*").eq("key", "shop_settings").execute()
        
        if existing_result.data and len(existing_result.data) > 0:
            # 既存設定を更新
            existing_settings = json.loads(existing_result.data[0].get("value", "{}"))
            existing_obj = ShopSettings(**existing_settings)
            
            # 更新データをマージ
            update_data = settings_update.dict(exclude_unset=True)
            updated_settings = existing_obj.dict()
            updated_settings.update(update_data)
            
            # データベースを更新
            db.table("settings").update({
                "value": json.dumps(updated_settings, ensure_ascii=False)
            }).eq("key", "shop_settings").execute()
            
            return ShopSettings(**updated_settings)
        else:
            # 新規作成
            default_settings = ShopSettings(shop_name="Yoyaku 予約システム")
            default_data = default_settings.dict()
            update_data = settings_update.dict(exclude_unset=True)
            default_data.update(update_data)
            
            db.table("settings").insert({
                "key": "shop_settings",
                "value": json.dumps(default_data, ensure_ascii=False)
            }).execute()
            
            return ShopSettings(**default_data)
    except Exception as e:
        logger.error(f"設定更新エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"設定の更新に失敗しました: {str(e)}")


@router.post("/reset", response_model=ShopSettings)
async def reset_settings(db: Client = Depends(get_db)):
    """店舗設定をリセット（デフォルト値に戻す）"""
    try:
        default_settings = ShopSettings(shop_name="Yoyaku 予約システム")
        default_data = default_settings.dict()
        
        existing_result = db.table("settings").select("*").eq("key", "shop_settings").execute()
        
        if existing_result.data and len(existing_result.data) > 0:
            db.table("settings").update({
                "value": json.dumps(default_data, ensure_ascii=False)
            }).eq("key", "shop_settings").execute()
        else:
            db.table("settings").insert({
                "key": "shop_settings",
                "value": json.dumps(default_data, ensure_ascii=False)
            }).execute()
        
        return ShopSettings(**default_data)
    except Exception as e:
        logger.error(f"設定リセットエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"設定のリセットに失敗しました: {str(e)}")





