"""
予約管理APIルート
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from supabase import Client
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api.database import get_db
from api.auth import get_current_shop
from api.schemas import (
    ReservationCreate,
    ReservationUpdate,
    ReservationResponse,
    ReservationWithDetails,
    PaginationParams,
    PaginatedResponse,
    MessageResponse
)
from api.models import ReservationStatus
from api.email_service import get_email_service
from api.logger import logger
from config import settings

router = APIRouter()


def validate_reservation_datetime(reservation_datetime: datetime) -> None:
    """予約日時のバリデーション"""
    now = datetime.now()
    min_datetime = now + timedelta(hours=settings.MIN_ADVANCE_BOOKING_HOURS)
    max_datetime = now + timedelta(days=settings.MAX_ADVANCE_BOOKING_DAYS)
    
    if reservation_datetime < min_datetime:
        raise HTTPException(
            status_code=400,
            detail=f"予約は{settings.MIN_ADVANCE_BOOKING_HOURS}時間前までに必要です"
        )
    
    if reservation_datetime > max_datetime:
        raise HTTPException(
            status_code=400,
            detail=f"予約は{settings.MAX_ADVANCE_BOOKING_DAYS}日先まで可能です"
        )
    
    # 営業時間のチェック（簡易版）
    hour = reservation_datetime.hour
    if hour < int(settings.BUSINESS_HOURS_START.split(':')[0]) or \
       hour >= int(settings.BUSINESS_HOURS_END.split(':')[0]):
        raise HTTPException(
            status_code=400,
            detail=f"営業時間は{settings.BUSINESS_HOURS_START}～{settings.BUSINESS_HOURS_END}です"
        )


@router.post("/", response_model=ReservationResponse)
async def create_reservation(
    reservation: ReservationCreate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """予約を作成"""
    # 日時のバリデーション
    validate_reservation_datetime(reservation.reservation_datetime)
    
    # 顧客の存在確認と所有権チェック
    customer = db.table("customers").select("*").eq("id", reservation.customer_id).eq("shop_id", current_shop["id"]).execute()
    if not customer.data:
        raise HTTPException(status_code=404, detail="顧客が見つかりません")
    
    # サービスの存在確認と所有権チェック
    service = db.table("services").select("*").eq("id", reservation.service_id).eq("shop_id", current_shop["id"]).execute()
    if not service.data:
        raise HTTPException(status_code=404, detail="サービスが見つかりません")
    
    # スタイリストの存在確認と所有権チェック（指定されている場合）
    if reservation.stylist_id:
        stylist = db.table("stylists").select("*").eq("id", reservation.stylist_id).eq("shop_id", current_shop["id"]).execute()
        if not stylist.data:
            raise HTTPException(status_code=404, detail="スタイリストが見つかりません")
    
    # 重複予約のチェック（同じ店舗内で）
    existing = db.table("reservations").select("*").eq(
        "reservation_datetime", reservation.reservation_datetime.isoformat()
    ).eq("status", ReservationStatus.CONFIRMED.value).eq("shop_id", current_shop["id"]).execute()
    
    if existing.data:
        raise HTTPException(status_code=400, detail="この時間帯は既に予約が入っています")
    
    # 予約の作成
    reservation_data = reservation.dict()
    reservation_data["status"] = ReservationStatus.PENDING.value
    reservation_data["shop_id"] = current_shop["id"]
    
    result = db.table("reservations").insert(reservation_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="予約の作成に失敗しました")
    
    reservation_response = ReservationResponse(**result.data[0])
    
    # 予約確認メールを送信
    try:
        email_service = get_email_service()
        email_service.send_reservation_confirmation(
            customer_email=customer.data[0]["email"],
            customer_name=customer.data[0].get("name", "お客様"),
            reservation_datetime=reservation.reservation_datetime,
            service_name=service.data[0]["name"],
            stylist_name=stylist.data[0]["name"] if reservation.stylist_id and stylist.data else None,
            reservation_id=reservation_response.id
        )
        logger.info(f"予約 {reservation_response.id} の確認メールを送信しました")
    except Exception as e:
        logger.error(f"予約確認メールの送信に失敗しました: {str(e)}")
        # メール送信失敗は予約作成を阻害しない
    
    return reservation_response


@router.get("/", response_model=PaginatedResponse)
async def list_reservations(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    customer_id: Optional[str] = None,
    stylist_id: Optional[str] = None,
    status: Optional[ReservationStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """予約一覧を取得"""
    query = db.table("reservations").select("*").eq("shop_id", current_shop["id"])
    
    if customer_id:
        query = query.eq("customer_id", customer_id)
    if stylist_id:
        query = query.eq("stylist_id", stylist_id)
    if status:
        query = query.eq("status", status.value)
    if start_date:
        query = query.gte("reservation_datetime", start_date.isoformat())
    if end_date:
        query = query.lte("reservation_datetime", end_date.isoformat())
    
    # ページネーション
    from_index = (page - 1) * page_size
    to_index = from_index + page_size
    
    result = query.order("reservation_datetime", desc=False).execute()
    
    total = len(result.data)
    items = result.data[from_index:to_index]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{reservation_id}", response_model=ReservationWithDetails)
async def get_reservation(
    reservation_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """予約詳細を取得"""
    result = db.table("reservations").select("*").eq("id", reservation_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="予約が見つかりません")
    
    reservation = result.data[0]
    
    # 関連データの取得
    customer = None
    stylist = None
    service = None
    
    if reservation.get("customer_id"):
        customer_result = db.table("customers").select("*").eq("id", reservation["customer_id"]).execute()
        if customer_result.data:
            customer = customer_result.data[0]
    
    if reservation.get("stylist_id"):
        stylist_result = db.table("stylists").select("*").eq("id", reservation["stylist_id"]).execute()
        if stylist_result.data:
            stylist = stylist_result.data[0]
    
    if reservation.get("service_id"):
        service_result = db.table("services").select("*").eq("id", reservation["service_id"]).execute()
        if service_result.data:
            service = service_result.data[0]
    
    return ReservationWithDetails(
        **reservation,
        customer=customer,
        stylist=stylist,
        service=service
    )


@router.patch("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: str,
    reservation_update: ReservationUpdate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """予約を更新"""
    # 予約の存在確認と所有権チェック
    existing = db.table("reservations").select("*").eq("id", reservation_id).eq("shop_id", current_shop["id"]).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="予約が見つかりません")
    
    # 日時のバリデーション（更新される場合）
    if reservation_update.reservation_datetime:
        validate_reservation_datetime(reservation_update.reservation_datetime)
    
    # 更新データの準備
    update_data = reservation_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    # 予約の更新
    result = db.table("reservations").update(update_data).eq("id", reservation_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="予約の更新に失敗しました")
    
    return ReservationResponse(**result.data[0])


@router.post("/{reservation_id}/confirm", response_model=ReservationResponse)
async def confirm_reservation(
    reservation_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """予約を確認済みにする"""
    # 予約情報を取得（関連データ含む）
    reservation_result = db.table("reservations").select(
        "*, customers(*), services(*), stylists(*)"
    ).eq("id", reservation_id).eq("shop_id", current_shop["id"]).execute()
    
    if not reservation_result.data:
        raise HTTPException(status_code=404, detail="予約が見つかりません")
    
    reservation = reservation_result.data[0]
    
    result = db.table("reservations").update({
        "status": ReservationStatus.CONFIRMED.value,
        "updated_at": datetime.now().isoformat()
    }).eq("id", reservation_id).eq("shop_id", current_shop["id"]).execute()
    
    # 確認メールを送信
    try:
        customer = reservation.get("customers")
        service = reservation.get("services")
        stylist = reservation.get("stylists")
        
        if customer and service:
            email_service = get_email_service()
            email_service.send_reservation_confirmation(
                customer_email=customer.get("email"),
                customer_name=customer.get("name", "お客様"),
                reservation_datetime=datetime.fromisoformat(reservation["reservation_datetime"]),
                service_name=service.get("name", ""),
                stylist_name=stylist.get("name") if stylist else None,
                reservation_id=reservation_id
            )
            logger.info(f"予約 {reservation_id} の確認メールを送信しました")
    except Exception as e:
        logger.error(f"予約確認メールの送信に失敗しました: {str(e)}")
    
    return ReservationResponse(**result.data[0])


@router.post("/{reservation_id}/cancel", response_model=ReservationResponse)
async def cancel_reservation(
    reservation_id: str,
    reason: Optional[str] = None,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """予約をキャンセル"""
    # 予約の存在確認と所有権チェック
    existing = db.table("reservations").select("*").eq("id", reservation_id).eq("shop_id", current_shop["id"]).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="予約が見つかりません")
    
    reservation = existing.data[0]
    reservation_datetime = datetime.fromisoformat(reservation["reservation_datetime"])
    now = datetime.now()
    
    # キャンセル期限のチェック
    hours_before = (reservation_datetime - now).total_seconds() / 3600
    if hours_before < settings.CANCELLATION_HOURS_BEFORE:
        raise HTTPException(
            status_code=400,
            detail=f"予約の{settings.CANCELLATION_HOURS_BEFORE}時間前までにキャンセルしてください"
        )
    
    # 予約情報を取得（関連データ含む）
    reservation_full = db.table("reservations").select(
        "*, customers(*), services(*)"
    ).eq("id", reservation_id).eq("shop_id", current_shop["id"]).execute()
    
    # 予約のキャンセル
    result = db.table("reservations").update({
        "status": ReservationStatus.CANCELLED.value,
        "cancellation_reason": reason,
        "cancelled_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }).eq("id", reservation_id).eq("shop_id", current_shop["id"]).execute()
    
    # キャンセル確認メールを送信
    try:
        if reservation_full.data:
            reservation_data = reservation_full.data[0]
            customer = reservation_data.get("customers")
            service = reservation_data.get("services")
            
            if customer and service:
                email_service = get_email_service()
                email_service.send_reservation_cancellation(
                    customer_email=customer.get("email"),
                    customer_name=customer.get("name", "お客様"),
                    reservation_datetime=datetime.fromisoformat(reservation_data["reservation_datetime"]),
                    service_name=service.get("name", ""),
                    reason=reason
                )
                logger.info(f"予約 {reservation_id} のキャンセル確認メールを送信しました")
    except Exception as e:
        logger.error(f"キャンセル確認メールの送信に失敗しました: {str(e)}")
    
    return ReservationResponse(**result.data[0])


@router.delete("/{reservation_id}", response_model=MessageResponse)
async def delete_reservation(
    reservation_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """予約を削除（論理削除）"""
    result = db.table("reservations").update({
        "status": ReservationStatus.CANCELLED.value,
        "updated_at": datetime.now().isoformat()
    }).eq("id", reservation_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="予約が見つかりません")
    
    return MessageResponse(message="予約を削除しました")


@router.get("/availability/slots")
async def get_available_slots(
    date: str = Query(..., description="日付 (YYYY-MM-DD)"),
    service_id: Optional[str] = None,
    stylist_id: Optional[str] = None,
    db: Client = Depends(get_db)
):
    """指定日の利用可能な時間枠を取得"""
    try:
        target_date = datetime.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="無効な日付形式です")
    
    # 営業時間の取得
    start_hour = int(settings.BUSINESS_HOURS_START.split(':')[0])
    end_hour = int(settings.BUSINESS_HOURS_END.split(':')[0])
    slot_duration = settings.RESERVATION_SLOT_DURATION_MINUTES
    
    # 時間枠の生成
    slots = []
    current_time = target_date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end_time = target_date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    
    while current_time < end_time:
        slot_end = current_time + timedelta(minutes=slot_duration)
        
        # 既存の予約をチェック
        query = db.table("reservations").select("*").eq(
            "reservation_datetime", current_time.isoformat()
        ).in_("status", [ReservationStatus.PENDING.value, ReservationStatus.CONFIRMED.value])
        
        if service_id:
            query = query.eq("service_id", service_id)
        if stylist_id:
            query = query.eq("stylist_id", stylist_id)
        
        existing = query.execute()
        
        slots.append({
            "start_time": current_time.isoformat(),
            "end_time": slot_end.isoformat(),
            "available": len(existing.data) == 0
        })
        
        current_time = slot_end
    
    return {"date": date, "slots": slots}


