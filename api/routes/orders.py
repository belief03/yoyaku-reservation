"""
注文管理APIルート
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
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderWithDetails,
    PaginationParams,
    PaginatedResponse,
    MessageResponse,
    CouponValidateRequest
)
from api.models import OrderStatus
from api.routes import coupons
from api.email_service import get_email_service
from api.logger import logger

router = APIRouter()


def calculate_order_totals(items: list, discount_amount: int = 0) -> dict:
    """注文の合計金額を計算"""
    total_amount = sum(item["quantity"] * item["unit_price"] for item in items)
    final_amount = max(0, total_amount - discount_amount)
    
    return {
        "total_amount": total_amount,
        "discount_amount": discount_amount,
        "final_amount": final_amount
    }


@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """注文を作成"""
    # 顧客の存在確認と所有権チェック
    customer = db.table("customers").select("*").eq("id", order.customer_id).eq("shop_id", current_shop["id"]).execute()
    if not customer.data:
        raise HTTPException(status_code=404, detail="顧客が見つかりません")
    
    # 予約の存在確認と所有権チェック（指定されている場合）
    if order.reservation_id:
        reservation = db.table("reservations").select("*").eq("id", order.reservation_id).eq("shop_id", current_shop["id"]).execute()
        if not reservation.data:
            raise HTTPException(status_code=404, detail="予約が見つかりません")
    
    # アイテムの検証と所有権チェック
    for item in order.items:
        if item.product_id:
            product = db.table("products").select("*").eq("id", item.product_id).eq("shop_id", current_shop["id"]).execute()
            if not product.data:
                raise HTTPException(status_code=404, detail=f"商品 {item.product_id} が見つかりません")
            # 在庫チェック
            if product.data[0].get("stock_quantity") is not None:
                if product.data[0]["stock_quantity"] < item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"商品 {item.name} の在庫が不足しています"
                    )
        
        if item.service_id:
            service = db.table("services").select("*").eq("id", item.service_id).eq("shop_id", current_shop["id"]).execute()
            if not service.data:
                raise HTTPException(status_code=404, detail=f"サービス {item.service_id} が見つかりません")
    
    # クーポンの検証と適用
    discount_amount = 0
    if order.coupon_code:
        # クーポンの検証（同じ店舗内で）
        coupon_result = db.table("coupons").select("*").eq("code", order.coupon_code).eq("shop_id", current_shop["id"]).execute()
        
        if not coupon_result.data:
            raise HTTPException(status_code=400, detail="クーポンが見つかりません")
        
        coupon = coupon_result.data[0]
        total_amount = sum(item.quantity * item.unit_price for item in order.items)
        
        # クーポンの有効性チェック
        if not coupon.get("is_active", False):
            raise HTTPException(status_code=400, detail="このクーポンは無効です")
        
        from datetime import datetime
        now = datetime.now()
        valid_from = datetime.fromisoformat(coupon["valid_from"].replace("Z", "+00:00"))
        valid_until = datetime.fromisoformat(coupon["valid_until"].replace("Z", "+00:00"))
        
        if now < valid_from or now > valid_until:
            raise HTTPException(status_code=400, detail="このクーポンの有効期限が切れています")
        
        # 使用回数制限のチェック
        if coupon.get("usage_limit") and coupon.get("usage_count", 0) >= coupon["usage_limit"]:
            raise HTTPException(status_code=400, detail="このクーポンの使用回数制限に達しています")
        
        # 最小購入金額のチェック
        if coupon.get("min_purchase_amount") and total_amount < coupon["min_purchase_amount"]:
            raise HTTPException(
                status_code=400,
                detail=f"このクーポンは{coupon['min_purchase_amount']}円以上の購入でご利用いただけます"
            )
        
        # 割引金額の計算
        from api.utils import calculate_discount
        discount_amount = calculate_discount(
            total_amount,
            coupon["coupon_type"],
            coupon["discount_value"],
            coupon.get("max_discount_amount")
        )
        if not coupon_validation.valid:
            raise HTTPException(status_code=400, detail=coupon_validation.message or "無効なクーポンです")
        discount_amount = coupon_validation.discount_amount
    
    # 合計金額の計算
    items_data = [item.dict() for item in order.items]
    totals = calculate_order_totals(items_data, discount_amount)
    
    # 注文の作成
    order_data = {
        "customer_id": order.customer_id,
        "reservation_id": order.reservation_id,
        "items": items_data,
        "total_amount": totals["total_amount"],
        "discount_amount": totals["discount_amount"],
        "final_amount": totals["final_amount"],
        "status": OrderStatus.PENDING.value,
        "payment_method": order.payment_method,
        "notes": order.notes,
        "shop_id": current_shop["id"]
    }
    
    result = db.table("orders").insert(order_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="注文の作成に失敗しました")
    
    # 在庫の更新
    for item in order.items:
        if item.product_id:
            product = db.table("products").select("*").eq("id", item.product_id).eq("shop_id", current_shop["id"]).execute()
            if product.data and product.data[0].get("stock_quantity") is not None:
                new_stock = product.data[0]["stock_quantity"] - item.quantity
                db.table("products").update({
                    "stock_quantity": new_stock,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", item.product_id).eq("shop_id", current_shop["id"]).execute()
    
    # クーポン使用履歴の記録
    if order.coupon_code and discount_amount > 0:
        coupon_result = db.table("coupons").select("*").eq("code", order.coupon_code).eq("shop_id", current_shop["id"]).execute()
        if coupon_result.data:
            coupon_id = coupon_result.data[0]["id"]
            db.table("coupon_usages").insert({
                "coupon_id": coupon_id,
                "customer_id": order.customer_id,
                "order_id": result.data[0]["id"],
                "discount_amount": discount_amount,
                "used_at": datetime.now().isoformat(),
                "shop_id": current_shop["id"]
            }).execute()
            
            # クーポンの使用回数を更新
            db.table("coupons").update({
                "usage_count": coupon_result.data[0]["usage_count"] + 1,
                "updated_at": datetime.now().isoformat()
            }).eq("id", coupon_id).eq("shop_id", current_shop["id"]).execute()
    
    order_response = OrderResponse(**result.data[0])
    
    # 注文確認メールを送信
    try:
        email_service = get_email_service()
        email_service.send_order_confirmation(
            customer_email=customer.data[0]["email"],
            customer_name=customer.data[0].get("name", "お客様"),
            order_id=order_response.id,
            total_amount=order_response.final_amount,
            items=items_data
        )
        logger.info(f"注文 {order_response.id} の確認メールを送信しました")
    except Exception as e:
        logger.error(f"注文確認メールの送信に失敗しました: {str(e)}")
    
    return order_response


@router.get("/", response_model=PaginatedResponse)
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    customer_id: Optional[str] = None,
    reservation_id: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """注文一覧を取得"""
    query = db.table("orders").select("*").eq("shop_id", current_shop["id"])
    
    if customer_id:
        query = query.eq("customer_id", customer_id)
    if reservation_id:
        query = query.eq("reservation_id", reservation_id)
    if status:
        query = query.eq("status", status.value)
    if start_date:
        query = query.gte("created_at", start_date.isoformat())
    if end_date:
        query = query.lte("created_at", end_date.isoformat())
    
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


@router.get("/{order_id}", response_model=OrderWithDetails)
async def get_order(
    order_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """注文詳細を取得"""
    result = db.table("orders").select("*").eq("id", order_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="注文が見つかりません")
    
    order = result.data[0]
    
    # 関連データの取得
    customer = None
    reservation = None
    
    if order.get("customer_id"):
        customer_result = db.table("customers").select("*").eq("id", order["customer_id"]).execute()
        if customer_result.data:
            customer = customer_result.data[0]
    
    if order.get("reservation_id"):
        reservation_result = db.table("reservations").select("*").eq("id", order["reservation_id"]).execute()
        if reservation_result.data:
            reservation = reservation_result.data[0]
    
    return OrderWithDetails(
        **order,
        customer=customer,
        reservation=reservation
    )


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """注文を更新"""
    # 注文の存在確認と所有権チェック
    existing = db.table("orders").select("*").eq("id", order_id).eq("shop_id", current_shop["id"]).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="注文が見つかりません")
    
    update_data = order_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    result = db.table("orders").update(update_data).eq("id", order_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="注文の更新に失敗しました")
    
    return OrderResponse(**result.data[0])


@router.post("/{order_id}/pay", response_model=OrderResponse)
async def process_payment(
    order_id: str,
    payment_method: str = Query(..., description="支払い方法"),
    payment_id: Optional[str] = None,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """注文の支払いを処理"""
    result = db.table("orders").update({
        "status": OrderStatus.PAID.value,
        "payment_method": payment_method,
        "payment_id": payment_id,
        "updated_at": datetime.now().isoformat()
    }).eq("id", order_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="注文が見つかりません")
    
    return OrderResponse(**result.data[0])


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """注文をキャンセル"""
    # 注文の存在確認と所有権チェック
    existing = db.table("orders").select("*").eq("id", order_id).eq("shop_id", current_shop["id"]).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="注文が見つかりません")
    
    order = existing.data[0]
    
    # 在庫の戻し
    if order.get("items"):
        for item in order["items"]:
            if item.get("product_id"):
                product = db.table("products").select("*").eq("id", item["product_id"]).eq("shop_id", current_shop["id"]).execute()
                if product.data and product.data[0].get("stock_quantity") is not None:
                    new_stock = product.data[0]["stock_quantity"] + item["quantity"]
                    db.table("products").update({
                        "stock_quantity": new_stock,
                        "updated_at": datetime.now().isoformat()
                    }).eq("id", item["product_id"]).eq("shop_id", current_shop["id"]).execute()
    
    # 注文のキャンセル
    result = db.table("orders").update({
        "status": OrderStatus.CANCELLED.value,
        "updated_at": datetime.now().isoformat()
    }).eq("id", order_id).eq("shop_id", current_shop["id"]).execute()
    
    return OrderResponse(**result.data[0])

