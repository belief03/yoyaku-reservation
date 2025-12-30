"""
クーポン管理APIルート
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
from supabase import Client
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api.database import get_db
from api.auth import get_current_shop
from api.schemas import (
    CouponCreate,
    CouponUpdate,
    CouponResponse,
    CouponValidateRequest,
    CouponValidateResponse,
    PaginationParams,
    PaginatedResponse,
    MessageResponse
)
from api.models import CouponType

router = APIRouter()


@router.post("/", response_model=CouponResponse)
async def create_coupon(
    coupon: CouponCreate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """クーポンを作成"""
    # コードの重複チェック（同じ店舗内で）
    existing = db.table("coupons").select("*").eq("code", coupon.code).eq("shop_id", current_shop["id"]).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="このクーポンコードは既に使用されています")
    
    coupon_data = coupon.dict()
    coupon_data["usage_count"] = 0
    coupon_data["shop_id"] = current_shop["id"]
    result = db.table("coupons").insert(coupon_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="クーポンの作成に失敗しました")
    
    return CouponResponse(**result.data[0])


@router.get("/", response_model=PaginatedResponse)
async def list_coupons(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = None,
    coupon_type: Optional[CouponType] = None,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """クーポン一覧を取得"""
    query = db.table("coupons").select("*").eq("shop_id", current_shop["id"])
    
    if is_active is not None:
        query = query.eq("is_active", is_active)
    if coupon_type:
        query = query.eq("coupon_type", coupon_type.value)
    
    # ページネーション
    from_index = (page - 1) * page_size
    to_index = from_index + page_size
    
    result = query.order("created_at", desc=True).execute()
    
    total = len(result.data)
    items = result.data[from_index:to_index]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{coupon_id}", response_model=CouponResponse)
async def get_coupon(
    coupon_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """クーポン詳細を取得"""
    result = db.table("coupons").select("*").eq("id", coupon_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="クーポンが見つかりません")
    
    return CouponResponse(**result.data[0])


@router.patch("/{coupon_id}", response_model=CouponResponse)
async def update_coupon(
    coupon_id: str,
    coupon_update: CouponUpdate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """クーポン情報を更新"""
    # クーポンの存在確認と所有権チェック
    existing = db.table("coupons").select("*").eq("id", coupon_id).eq("shop_id", current_shop["id"]).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="クーポンが見つかりません")
    
    update_data = coupon_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    result = db.table("coupons").update(update_data).eq("id", coupon_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="クーポン情報の更新に失敗しました")
    
    return CouponResponse(**result.data[0])


@router.delete("/{coupon_id}", response_model=MessageResponse)
async def delete_coupon(
    coupon_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """クーポンを削除（論理削除）"""
    result = db.table("coupons").update({
        "is_active": False,
        "updated_at": datetime.now().isoformat()
    }).eq("id", coupon_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="クーポンが見つかりません")
    
    return MessageResponse(message="クーポンを削除しました")


@router.post("/validate", response_model=CouponValidateResponse)
async def validate_coupon(
    validation_request: CouponValidateRequest,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """クーポンの有効性を検証"""
    # クーポンの取得（同じ店舗内で）
    result = db.table("coupons").select("*").eq("code", validation_request.code).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        return CouponValidateResponse(
            valid=False,
            message="クーポンが見つかりません"
        )
    
    coupon = result.data[0]
    
    # アクティブチェック
    if not coupon.get("is_active", False):
        return CouponValidateResponse(
            valid=False,
            message="このクーポンは無効です"
        )
    
    # 有効期限チェック
    now = datetime.now()
    valid_from = datetime.fromisoformat(coupon["valid_from"])
    valid_until = datetime.fromisoformat(coupon["valid_until"])
    
    if now < valid_from:
        return CouponValidateResponse(
            valid=False,
            message="このクーポンはまだ有効ではありません"
        )
    
    if now > valid_until:
        return CouponValidateResponse(
            valid=False,
            message="このクーポンの有効期限が切れています"
        )
    
    # 使用回数制限チェック
    if coupon.get("usage_limit") is not None:
        if coupon.get("usage_count", 0) >= coupon["usage_limit"]:
            return CouponValidateResponse(
                valid=False,
                message="このクーポンの使用回数制限に達しています"
            )
    
    # 最低購入金額チェック
    if coupon.get("min_purchase_amount") is not None:
        if validation_request.total_amount < coupon["min_purchase_amount"]:
            return CouponValidateResponse(
                valid=False,
                message=f"最低購入金額 {coupon['min_purchase_amount']}円以上でご利用いただけます"
            )
    
    # 適用可能サービスチェック
    if coupon.get("applicable_services") and validation_request.service_ids:
        applicable = set(coupon["applicable_services"])
        requested = set(validation_request.service_ids)
        if not requested.intersection(applicable):
            return CouponValidateResponse(
                valid=False,
                message="このクーポンは選択されたサービスには適用できません"
            )
    
    # 割引金額の計算
    discount_amount = 0
    if coupon["coupon_type"] == CouponType.PERCENTAGE.value:
        discount_amount = int(validation_request.total_amount * coupon["discount_value"] / 100)
        if coupon.get("max_discount_amount"):
            discount_amount = min(discount_amount, coupon["max_discount_amount"])
    elif coupon["coupon_type"] == CouponType.FIXED_AMOUNT.value:
        discount_amount = coupon["discount_value"]
    
    return CouponValidateResponse(
        valid=True,
        coupon=CouponResponse(**coupon),
        discount_amount=discount_amount,
        message="クーポンが適用されました"
    )


@router.get("/code/{code}", response_model=CouponResponse)
async def get_coupon_by_code(
    code: str,
    db: Client = Depends(get_db)
):
    """クーポンコードでクーポンを取得"""
    result = db.table("coupons").select("*").eq("code", code).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="クーポンが見つかりません")
    
    return CouponResponse(**result.data[0])




