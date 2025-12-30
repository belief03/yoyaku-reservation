"""
顧客管理APIルート
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from supabase import Client
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api.database import get_db
from api.auth import get_current_shop
from api.schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    PaginationParams,
    PaginatedResponse,
    MessageResponse
)

router = APIRouter()


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """顧客を作成"""
    # メールアドレスの重複チェック（同じ店舗内で）
    existing = db.table("customers").select("*").eq("email", customer.email).eq("shop_id", current_shop["id"]).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="このメールアドレスは既に登録されています")
    
    customer_data = customer.dict()
    customer_data["shop_id"] = current_shop["id"]
    result = db.table("customers").insert(customer_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="顧客の作成に失敗しました")
    
    return CustomerResponse(**result.data[0])


@router.get("/", response_model=PaginatedResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    email: Optional[str] = None,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """顧客一覧を取得"""
    query = db.table("customers").select("*").eq("shop_id", current_shop["id"])
    
    if email:
        query = query.eq("email", email)
    if name:
        query = query.ilike("name", f"%{name}%")
    if is_active is not None:
        query = query.eq("is_active", is_active)
    
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


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """顧客詳細を取得"""
    result = db.table("customers").select("*").eq("id", customer_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="顧客が見つかりません")
    
    # IDを文字列に変換（データベースが整数型の場合）
    data = result.data[0].copy()
    if isinstance(data.get("id"), int):
        data["id"] = str(data["id"])
    
    # 必須フィールドのデフォルト値を設定
    if "is_active" not in data:
        data["is_active"] = True
    if "total_visits" not in data:
        data["total_visits"] = 0
    
    return CustomerResponse(**data)


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_update: CustomerUpdate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """顧客情報を更新"""
    # 顧客の存在確認と所有権チェック
    existing = db.table("customers").select("*").eq("id", customer_id).eq("shop_id", current_shop["id"]).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="顧客が見つかりません")
    
    update_data = customer_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    result = db.table("customers").update(update_data).eq("id", customer_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="顧客情報の更新に失敗しました")
    
    return CustomerResponse(**result.data[0])


@router.delete("/{customer_id}", response_model=MessageResponse)
async def delete_customer(
    customer_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """顧客を削除（論理削除）"""
    result = db.table("customers").update({
        "is_active": False,
        "updated_at": datetime.now().isoformat()
    }).eq("id", customer_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="顧客が見つかりません")
    
    return MessageResponse(message="顧客を削除しました")


@router.get("/{customer_id}/reservations")
async def get_customer_reservations(
    customer_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """顧客の予約履歴を取得"""
    # 顧客の存在確認と所有権チェック
    customer = db.table("customers").select("*").eq("id", customer_id).eq("shop_id", current_shop["id"]).execute()
    if not customer.data:
        raise HTTPException(status_code=404, detail="顧客が見つかりません")
    
    # 予約の取得
    from_index = (page - 1) * page_size
    to_index = from_index + page_size
    
    result = db.table("reservations").select("*").eq(
        "customer_id", customer_id
    ).eq("shop_id", current_shop["id"]).order("reservation_datetime", desc=True).execute()
    
    total = len(result.data)
    items = result.data[from_index:to_index]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{customer_id}/orders")
async def get_customer_orders(
    customer_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """顧客の注文履歴を取得"""
    # 顧客の存在確認と所有権チェック
    customer = db.table("customers").select("*").eq("id", customer_id).eq("shop_id", current_shop["id"]).execute()
    if not customer.data:
        raise HTTPException(status_code=404, detail="顧客が見つかりません")
    
    # 注文の取得
    from_index = (page - 1) * page_size
    to_index = from_index + page_size
    
    result = db.table("orders").select("*").eq(
        "customer_id", customer_id
    ).eq("shop_id", current_shop["id"]).order("created_at", desc=True).execute()
    
    total = len(result.data)
    items = result.data[from_index:to_index]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


