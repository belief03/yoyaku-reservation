"""
予約リマインダー送信スクリプト
指定時間前に予約がある顧客にリマインダーメールを送信
"""
import sys
import os
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.supabase_client import supabase
from api.email_service import get_email_service
from api.models import ReservationStatus
from config import settings
from api.logger import logger


def send_reservation_reminders(hours_before: int = 24):
    """
    予約リマインダーを送信
    
    Args:
        hours_before: 何時間前に送信するか
    """
    logger.info(f"予約リマインダーの送信を開始します（{hours_before}時間前）")
    
    # 送信対象の日時範囲を計算
    now = datetime.now()
    target_start = now + timedelta(hours=hours_before - 1)
    target_end = now + timedelta(hours=hours_before + 1)
    
    # リマインダー未送信の予約を取得
    reservations = supabase.table("reservations").select(
        "*, customers(*), services(*), stylists(*)"
    ).in_("status", [
        ReservationStatus.PENDING.value,
        ReservationStatus.CONFIRMED.value
    ]).gte(
        "reservation_datetime", target_start.isoformat()
    ).lte(
        "reservation_datetime", target_end.isoformat()
    ).eq("reminder_sent", False).execute()
    
    if not reservations.data:
        logger.info("送信対象の予約がありません")
        return
    
    email_service = get_email_service()
    sent_count = 0
    error_count = 0
    
    for reservation in reservations.data:
        try:
            customer = reservation.get("customers")
            service = reservation.get("services")
            
            if not customer or not service:
                logger.warning(f"予約 {reservation['id']} の関連データが見つかりません")
                continue
            
            customer_email = customer.get("email")
            if not customer_email:
                logger.warning(f"顧客 {customer.get('id')} のメールアドレスがありません")
                continue
            
            # リマインダーメールを送信
            success = email_service.send_reservation_reminder(
                customer_email=customer_email,
                customer_name=customer.get("name", "お客様"),
                reservation_datetime=datetime.fromisoformat(reservation["reservation_datetime"]),
                service_name=service.get("name", ""),
                hours_before=hours_before
            )
            
            if success:
                # リマインダー送信済みフラグを更新
                supabase.table("reservations").update({
                    "reminder_sent": True,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", reservation["id"]).execute()
                
                sent_count += 1
                logger.info(f"予約 {reservation['id']} のリマインダーを送信しました")
            else:
                error_count += 1
                logger.error(f"予約 {reservation['id']} のリマインダー送信に失敗しました")
        
        except Exception as e:
            error_count += 1
            logger.error(f"予約 {reservation.get('id', 'unknown')} の処理中にエラーが発生しました: {str(e)}")
    
    logger.info(f"リマインダー送信完了: 成功 {sent_count}件, 失敗 {error_count}件")


if __name__ == "__main__":
    # デフォルトは24時間前
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    send_reservation_reminders(hours)






